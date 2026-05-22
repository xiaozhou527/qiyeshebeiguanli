from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from apps.core.access import scope_assets
from apps.core.constants import ASSET_MANAGER_GROUP, EMPLOYEE_GROUP
from apps.core.models import Department, OperationLog

from .models import Asset, AssetCategory, BorrowRecord, MaintenanceRecord, ScrapRecord
from .services import borrow_asset, maintain_asset, return_asset, scrap_asset


class AssetServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="test123456")
        self.department = Department.objects.create(code="D100", name="测试部门")
        self.category = AssetCategory.objects.create(code="CAT100", name="测试分类")
        self.asset = Asset.objects.create(
            code="ASSET-001",
            name="测试电脑",
            category=self.category,
            department=self.department,
        )

    def test_asset_manager_only_sees_own_department_assets(self):
        other_department = Department.objects.create(code="D200", name="其他部门")
        manager = get_user_model().objects.create_user(username="manager", password="test123456")
        Group.objects.get_or_create(name=ASSET_MANAGER_GROUP)
        manager.groups.add(Group.objects.get(name=ASSET_MANAGER_GROUP))
        manager.profile.department = self.department
        manager.profile.save()
        Asset.objects.create(
            code="ASSET-002",
            name="其他部门电脑",
            category=self.category,
            department=other_department,
        )

        visible_assets = scope_assets(Asset.objects.all(), manager)

        self.assertEqual(visible_assets.count(), 1)
        self.assertEqual(visible_assets.first(), self.asset)

    def test_employee_only_sees_owned_assets(self):
        employee = get_user_model().objects.create_user(username="employee_scope", password="test123456")
        Group.objects.get_or_create(name=EMPLOYEE_GROUP)
        employee.groups.add(Group.objects.get(name=EMPLOYEE_GROUP))
        employee.profile.department = self.department
        employee.profile.save()
        self.asset.assignee = employee
        self.asset.save(update_fields=["assignee", "updated_at"])
        Asset.objects.create(
            code="ASSET-003",
            name="他人资产",
            category=self.category,
            department=self.department,
        )

        visible_assets = scope_assets(Asset.objects.all(), employee)

        self.assertEqual(visible_assets.count(), 1)
        self.assertEqual(visible_assets.first(), self.asset)

    def test_borrow_and_return_asset_updates_status(self):
        record = BorrowRecord.objects.create(
            asset=self.asset,
            borrower=self.user,
            department=self.department,
        )

        borrow_asset(record=record, operator=self.user)
        self.asset.refresh_from_db()
        record.refresh_from_db()

        self.assertEqual(self.asset.status, Asset.Status.IN_USE)
        self.assertEqual(self.asset.assignee, self.user)
        self.assertEqual(record.status, BorrowRecord.Status.BORROWED)

        return_asset(record=record, operator=self.user)
        self.asset.refresh_from_db()
        record.refresh_from_db()

        self.assertEqual(self.asset.status, Asset.Status.IDLE)
        self.assertIsNone(self.asset.assignee)
        self.assertEqual(record.status, BorrowRecord.Status.RETURNED)

    def test_maintenance_done_returns_asset_to_idle(self):
        record = MaintenanceRecord.objects.create(
            asset=self.asset,
            reported_by=self.user,
            issue_description="屏幕闪烁",
            status=MaintenanceRecord.Status.DONE,
        )

        maintain_asset(record=record, operator=self.user)
        self.asset.refresh_from_db()

        self.assertEqual(self.asset.status, Asset.Status.IDLE)

    def test_scrap_approved_marks_asset_scrapped_and_logs(self):
        record = ScrapRecord.objects.create(
            asset=self.asset,
            applicant=self.user,
            reason="设备损坏严重",
            approval_status=ScrapRecord.ApprovalStatus.APPROVED,
        )

        scrap_asset(record=record, operator=self.user)
        self.asset.refresh_from_db()

        self.assertEqual(self.asset.status, Asset.Status.SCRAPPED)
        self.assertTrue(
            OperationLog.objects.filter(
                target_type="scrap_record",
                target_id=str(record.pk),
            ).exists()
        )
