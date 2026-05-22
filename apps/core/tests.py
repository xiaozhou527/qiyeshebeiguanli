from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .access import can_register_asset_manager, can_register_employee
from .constants import ASSET_MANAGER_GROUP, EMPLOYEE_GROUP
from .models import Department, OperationLog, UserProfile
from .services import ensure_default_groups, log_operation
from .user_services import register_user


class CoreServiceTests(TestCase):
    def setUp(self):
        ensure_default_groups()

    def test_ensure_default_groups(self):
        ensure_default_groups()
        self.assertEqual(Group.objects.filter(name__in=["admin", "asset_manager", "employee"]).count(), 3)

    def test_log_operation_creates_record(self):
        user = get_user_model().objects.create_user(username="logger", password="demo123456")
        log_operation(
            user=user,
            action=OperationLog.ActionType.CREATE,
            target_type="asset",
            target_id="1",
            target_label="ASSET-001",
            message="创建资产",
        )
        self.assertTrue(OperationLog.objects.filter(user=user, target_type="asset").exists())

    def test_user_profile_is_created_with_user(self):
        user = get_user_model().objects.create_user(username="profile_user", password="demo123456")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_admin_can_register_asset_manager_only(self):
        admin = get_user_model().objects.create_superuser(
            username="admin_test", password="demo123456", email="admin@test.com"
        )
        self.assertTrue(can_register_asset_manager(admin))
        self.assertFalse(can_register_employee(admin))

    def test_asset_manager_can_register_employee_only(self):
        department = Department.objects.create(code="D500", name="测试部门")
        manager = get_user_model().objects.create_user(username="manager_test", password="demo123456")
        manager.groups.add(Group.objects.get(name=ASSET_MANAGER_GROUP))
        manager.profile.department = department
        manager.profile.save()

        self.assertFalse(can_register_asset_manager(manager))
        self.assertTrue(can_register_employee(manager))

    def test_register_user_records_creator_department_and_role(self):
        department = Department.objects.create(code="D600", name="注册部门")
        manager = get_user_model().objects.create_user(username="manager_scope", password="demo123456")
        manager.groups.add(Group.objects.get(name=ASSET_MANAGER_GROUP))
        manager.profile.department = department
        manager.profile.save()

        employee = get_user_model().objects.create_user(username="employee_scope2", password="demo123456")
        register_user(
            creator=manager,
            user=employee,
            role_name=EMPLOYEE_GROUP,
            title="测试员工",
            phone="13800000000",
        )

        employee.refresh_from_db()
        self.assertTrue(employee.groups.filter(name=EMPLOYEE_GROUP).exists())
        self.assertEqual(employee.profile.department, department)
        self.assertEqual(employee.profile.created_by, manager)


class RegistrationViewTests(TestCase):
    def setUp(self):
        ensure_default_groups()
        self.admin = get_user_model().objects.create_superuser(
            username="root_admin", password="demo123456", email="root@test.com"
        )
        self.department = Department.objects.create(code="D700", name="视图测试部门")
        self.manager = get_user_model().objects.create_user(username="view_manager", password="demo123456")
        self.manager.groups.add(Group.objects.get(name=ASSET_MANAGER_GROUP))
        self.manager.profile.department = self.department
        self.manager.profile.created_by = self.admin
        self.manager.profile.save()

    def test_admin_cannot_open_employee_registration_page(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("core:register_employee"))
        self.assertEqual(response.status_code, 403)

    def test_asset_manager_can_register_employee(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            reverse("core:register_employee"),
            {
                "username": "new_employee",
                "first_name": "新员工",
                "phone": "13900000000",
                "title": "库管员",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "department": self.department.name,
            },
        )
        self.assertEqual(response.status_code, 302)
        employee = get_user_model().objects.get(username="new_employee")
        self.assertTrue(employee.groups.filter(name=EMPLOYEE_GROUP).exists())
        self.assertEqual(employee.profile.department, self.department)
        self.assertEqual(employee.profile.created_by, self.manager)
