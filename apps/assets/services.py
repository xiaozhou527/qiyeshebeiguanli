from django.utils import timezone

from apps.core.models import OperationLog
from apps.core.services import build_request_meta, log_operation

from .models import Asset, BorrowRecord, MaintenanceRecord, ScrapRecord, TransferRecord


def create_asset(*, asset: Asset, operator, request=None):
    log_operation(
        user=operator,
        action=OperationLog.ActionType.CREATE,
        target_type="asset",
        target_id=asset.pk,
        target_label=str(asset),
        message="新增资产",
        detail={"status": asset.status},
        request_meta=build_request_meta(request),
    )
    return asset


def update_asset(*, asset: Asset, operator, request=None):
    log_operation(
        user=operator,
        action=OperationLog.ActionType.UPDATE,
        target_type="asset",
        target_id=asset.pk,
        target_label=str(asset),
        message="更新资产",
        detail={"status": asset.status},
        request_meta=build_request_meta(request),
    )
    return asset


def borrow_asset(*, record: BorrowRecord, operator, request=None):
    asset = record.asset
    asset.department = record.department
    asset.assignee = record.borrower
    asset.status = Asset.Status.IN_USE
    asset.save(update_fields=["department", "assignee", "status", "updated_at"])
    log_operation(
        user=operator,
        action=OperationLog.ActionType.BUSINESS,
        target_type="borrow_record",
        target_id=record.pk,
        target_label=str(record.asset),
        message="登记资产领用",
        detail={"asset": asset.code, "borrower": record.borrower.username},
        request_meta=build_request_meta(request),
    )
    return record


def return_asset(*, record: BorrowRecord, operator, request=None):
    record.returned_at = record.returned_at or timezone.now()
    record.status = BorrowRecord.Status.RETURNED
    record.save(update_fields=["returned_at", "status", "note", "updated_at"])
    asset = record.asset
    asset.assignee = None
    asset.status = Asset.Status.IDLE
    asset.save(update_fields=["assignee", "status", "updated_at"])
    log_operation(
        user=operator,
        action=OperationLog.ActionType.BUSINESS,
        target_type="borrow_record",
        target_id=record.pk,
        target_label=str(record.asset),
        message="登记资产归还",
        detail={"asset": asset.code, "borrower": record.borrower.username},
        request_meta=build_request_meta(request),
    )
    return record


def transfer_asset(*, record: TransferRecord, operator, request=None):
    asset = record.asset
    asset.department = record.to_department
    asset.assignee = record.to_user
    asset.save(update_fields=["department", "assignee", "updated_at"])
    log_operation(
        user=operator,
        action=OperationLog.ActionType.BUSINESS,
        target_type="transfer_record",
        target_id=record.pk,
        target_label=str(record.asset),
        message="登记资产调拨",
        detail={"from": record.from_department.code, "to": record.to_department.code},
        request_meta=build_request_meta(request),
    )
    return record


def maintain_asset(*, record: MaintenanceRecord, operator, request=None):
    asset = record.asset
    asset.status = (
        Asset.Status.REPAIRING if record.status != MaintenanceRecord.Status.DONE else Asset.Status.IDLE
    )
    asset.save(update_fields=["status", "updated_at"])
    log_operation(
        user=operator,
        action=OperationLog.ActionType.BUSINESS,
        target_type="maintenance_record",
        target_id=record.pk,
        target_label=str(record.asset),
        message="登记资产维修",
        detail={"status": record.status},
        request_meta=build_request_meta(request),
    )
    return record


def scrap_asset(*, record: ScrapRecord, operator, request=None):
    asset = record.asset
    if record.approval_status == ScrapRecord.ApprovalStatus.APPROVED:
        asset.status = Asset.Status.SCRAPPED
        asset.assignee = None
        asset.save(update_fields=["status", "assignee", "updated_at"])
    log_operation(
        user=operator,
        action=OperationLog.ActionType.BUSINESS,
        target_type="scrap_record",
        target_id=record.pk,
        target_label=str(record.asset),
        message="登记资产报废",
        detail={"approval_status": record.approval_status},
        request_meta=build_request_meta(request),
    )
    return record
