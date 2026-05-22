from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import TemplateView

from apps.assets.models import Asset, BorrowRecord, MaintenanceRecord, ScrapRecord
from apps.core.access import (
    get_user_department,
    is_asset_manager,
    scope_assets,
    scope_borrow_records,
    scope_departments,
    scope_maintenance_records,
    scope_operation_logs,
    scope_scrap_records,
)
from apps.core.models import Department, OperationLog


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        scoped_assets = scope_assets(Asset.objects.all(), user)
        scoped_departments = scope_departments(Department.objects.all(), user)
        scoped_borrow_records = scope_borrow_records(BorrowRecord.objects.all(), user)
        scoped_maintenances = scope_maintenance_records(MaintenanceRecord.objects.all(), user)
        scoped_scraps = scope_scrap_records(ScrapRecord.objects.all(), user)
        scoped_logs = scope_operation_logs(OperationLog.objects.select_related("user").all(), user)

        context["metrics"] = {
            "asset_total": scoped_assets.count(),
            "department_total": scoped_departments.count(),
            "borrowing_total": scoped_borrow_records.filter(status=BorrowRecord.Status.BORROWED).count(),
            "maintenance_total": scoped_maintenances.filter(
                status__in=[MaintenanceRecord.Status.PENDING, MaintenanceRecord.Status.PROCESSING]
            ).count(),
            "scrap_pending_total": scoped_scraps.filter(
                approval_status=ScrapRecord.ApprovalStatus.PENDING
            ).count(),
        }
        context["asset_status_stats"] = scoped_assets.values("status").annotate(total=Count("id")).order_by("status")
        context["latest_logs"] = scoped_logs[:8]
        context["latest_assets"] = scoped_assets.select_related("category", "department")[:8]
        context["can_manage"] = is_asset_manager(user)
        context["current_department"] = get_user_department(user)
        return context
