from rest_framework import viewsets

from apps.core.access import (
    scope_assets,
    scope_borrow_records,
    scope_departments,
    scope_maintenance_records,
    scope_scrap_records,
    scope_transfer_records,
)
from apps.core.api_permissions import ScopedAssetPermission
from apps.core.models import Department

from .models import Asset, AssetCategory, BorrowRecord, MaintenanceRecord, ScrapRecord, TransferRecord
from .serializers import (
    AssetCategorySerializer,
    AssetSerializer,
    BorrowRecordSerializer,
    DepartmentSerializer,
    MaintenanceRecordSerializer,
    ScrapRecordSerializer,
    TransferRecordSerializer,
)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [ScopedAssetPermission]


class DepartmentViewSet(BaseModelViewSet):
    serializer_class = DepartmentSerializer
    filterset_fields = ["is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "created_at"]

    def get_queryset(self):
        queryset = Department.objects.select_related("manager").all()
        return scope_departments(queryset, self.request.user)


class AssetCategoryViewSet(BaseModelViewSet):
    queryset = AssetCategory.objects.select_related("parent").all()
    serializer_class = AssetCategorySerializer
    filterset_fields = ["is_active", "parent"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "created_at"]


class AssetViewSet(BaseModelViewSet):
    serializer_class = AssetSerializer
    filterset_fields = ["status", "category", "department", "assignee"]
    search_fields = ["code", "name", "brand", "model", "location"]
    ordering_fields = ["code", "purchase_date", "created_at"]

    def get_queryset(self):
        queryset = Asset.objects.select_related("category", "department", "assignee").all()
        return scope_assets(queryset, self.request.user)


class BorrowRecordViewSet(BaseModelViewSet):
    serializer_class = BorrowRecordSerializer
    filterset_fields = ["status", "department", "borrower"]
    search_fields = ["asset__code", "asset__name", "borrower__username"]
    ordering_fields = ["borrowed_at", "returned_at", "created_at"]

    def get_queryset(self):
        queryset = BorrowRecord.objects.select_related("asset", "borrower", "department").all()
        return scope_borrow_records(queryset, self.request.user)


class TransferRecordViewSet(BaseModelViewSet):
    serializer_class = TransferRecordSerializer
    filterset_fields = ["from_department", "to_department"]
    search_fields = ["asset__code", "asset__name"]
    ordering_fields = ["transferred_at", "created_at"]

    def get_queryset(self):
        queryset = TransferRecord.objects.select_related(
            "asset", "from_department", "to_department", "from_user", "to_user"
        ).all()
        return scope_transfer_records(queryset, self.request.user)


class MaintenanceRecordViewSet(BaseModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    filterset_fields = ["status"]
    search_fields = ["asset__code", "asset__name", "maintenance_vendor", "maintainer"]
    ordering_fields = ["started_at", "completed_at", "created_at"]

    def get_queryset(self):
        queryset = MaintenanceRecord.objects.select_related("asset", "reported_by").all()
        return scope_maintenance_records(queryset, self.request.user)


class ScrapRecordViewSet(BaseModelViewSet):
    serializer_class = ScrapRecordSerializer
    filterset_fields = ["approval_status", "applicant", "approved_by"]
    search_fields = ["asset__code", "asset__name", "applicant__username"]
    ordering_fields = ["requested_at", "approved_at", "created_at"]

    def get_queryset(self):
        queryset = ScrapRecord.objects.select_related("asset", "applicant", "approved_by").all()
        return scope_scrap_records(queryset, self.request.user)
