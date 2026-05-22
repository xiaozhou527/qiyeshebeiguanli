from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.assets.models import Asset, AssetCategory
from apps.core.constants import ASSET_MANAGER_GROUP, EMPLOYEE_GROUP
from apps.core.models import Department, UserProfile
from apps.core.services import ensure_default_groups


class Command(BaseCommand):
    help = "初始化演示数据和默认账号"

    def handle(self, *args, **options):
        User = get_user_model()
        ensure_default_groups()

        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True},
        )
        admin_user.set_password("admin123456")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        manager_user, _ = User.objects.get_or_create(username="asset_manager")
        manager_user.set_password("manager123456")
        manager_user.is_staff = True
        manager_user.save()
        manager_user.groups.add(*Group.objects.filter(name__in=[ASSET_MANAGER_GROUP]))

        employee_user, _ = User.objects.get_or_create(username="employee")
        employee_user.set_password("employee123456")
        employee_user.save()
        employee_user.groups.add(*Group.objects.filter(name__in=[EMPLOYEE_GROUP]))

        office, _ = Department.objects.get_or_create(code="D001", defaults={"name": "综合办公室"})
        tech, _ = Department.objects.get_or_create(code="D002", defaults={"name": "信息技术部"})
        if office.manager_id != employee_user.id:
            office.manager = employee_user
            office.save(update_fields=["manager", "updated_at"])
        if tech.manager_id != manager_user.id:
            tech.manager = manager_user
            tech.save(update_fields=["manager", "updated_at"])

        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        admin_profile.title = "系统管理员"
        admin_profile.save()

        manager_profile, _ = UserProfile.objects.get_or_create(user=manager_user)
        manager_profile.department = tech
        manager_profile.created_by = admin_user
        manager_profile.title = "资产管理员"
        manager_profile.save()

        employee_profile, _ = UserProfile.objects.get_or_create(user=employee_user)
        employee_profile.department = office
        employee_profile.created_by = manager_user
        employee_profile.title = "普通员工"
        employee_profile.save()

        laptop, _ = AssetCategory.objects.get_or_create(code="IT-PC", defaults={"name": "电脑设备"})
        office_equipment, _ = AssetCategory.objects.get_or_create(
            code="OFFICE", defaults={"name": "办公设备"}
        )

        Asset.objects.get_or_create(
            code="A-2026-0001",
            defaults={
                "name": "办公笔记本电脑",
                "category": laptop,
                "brand": "Lenovo",
                "model": "ThinkPad T14",
                "purchase_price": Decimal("6800.00"),
                "department": tech,
                "assignee": manager_user,
                "status": Asset.Status.IN_USE,
                "location": "技术部办公区",
            },
        )
        Asset.objects.get_or_create(
            code="A-2026-0002",
            defaults={
                "name": "彩色打印机",
                "category": office_equipment,
                "brand": "HP",
                "model": "LaserJet Pro",
                "purchase_price": Decimal("3200.00"),
                "department": office,
                "status": Asset.Status.IDLE,
                "location": "行政文印室",
            },
        )
        Asset.objects.get_or_create(
            code="A-2026-0003",
            defaults={
                "name": "员工办公显示器",
                "category": office_equipment,
                "brand": "Dell",
                "model": "P2422H",
                "purchase_price": Decimal("1299.00"),
                "department": office,
                "assignee": employee_user,
                "status": Asset.Status.IN_USE,
                "location": "综合办公室工位A-12",
            },
        )

        self.stdout.write(self.style.SUCCESS("演示数据初始化完成。"))
