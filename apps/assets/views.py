from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.access import (
    get_user_department,
    is_admin,
    is_asset_manager,
    scope_assets,
    scope_borrow_records,
    scope_departments,
    scope_maintenance_records,
    scope_operation_logs,
    scope_scrap_records,
    scope_transfer_records,
)
from apps.core.mixins import DepartmentScopedManagerRequiredMixin
from apps.core.models import Department, OperationLog

from .forms import (
    AssetCategoryForm,
    AssetForm,
    BorrowRecordForm,
    DepartmentForm,
    MaintenanceRecordForm,
    ReturnBorrowRecordForm,
    ScrapRecordForm,
    TransferRecordForm,
)
from .models import Asset, AssetCategory, BorrowRecord, MaintenanceRecord, ScrapRecord, TransferRecord
from .services import borrow_asset, create_asset, maintain_asset, return_asset, scrap_asset, transfer_asset, update_asset


class ScopedFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = "assets/department_list.html"
    context_object_name = "departments"

    def get_queryset(self):
        queryset = Department.objects.select_related("manager").all()
        return scope_departments(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class DepartmentCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:department_list")
    extra_context = {"page_title": "新增部门"}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "部门已创建。")
        return response


class CategoryListView(LoginRequiredMixin, ListView):
    model = AssetCategory
    template_name = "assets/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return AssetCategory.objects.select_related("parent").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class CategoryCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:category_list")
    extra_context = {"page_title": "新增资产分类"}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "分类已创建。")
        return response


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 10

    def get_queryset(self):
        queryset = Asset.objects.select_related("category", "department", "assignee").order_by("code")
        queryset = scope_assets(queryset, self.request.user)
        search = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scoped_assets = scope_assets(Asset.objects.all(), self.request.user)
        context["status_choices"] = Asset.Status.choices
        context["summary"] = scoped_assets.values("status").annotate(total=Count("id")).order_by("status")
        context["can_manage"] = is_asset_manager(self.request.user)
        context["current_department"] = get_user_department(self.request.user)
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_queryset(self):
        return scope_assets(
            Asset.objects.select_related("category", "department", "assignee").all(),
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class AssetCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:asset_list")
    extra_context = {"page_title": "新增资产"}

    def form_valid(self, form):
        if not is_admin(self.request.user):
            form.instance.department = get_user_department(self.request.user)
        response = super().form_valid(form)
        create_asset(asset=self.object, operator=self.request.user, request=self.request)
        messages.success(self.request, "资产已创建。")
        return response


class AssetUpdateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:asset_list")
    extra_context = {"page_title": "编辑资产"}

    def get_queryset(self):
        return scope_assets(Asset.objects.all(), self.request.user)

    def form_valid(self, form):
        if not is_admin(self.request.user):
            form.instance.department = get_user_department(self.request.user)
        response = super().form_valid(form)
        update_asset(asset=self.object, operator=self.request.user, request=self.request)
        messages.success(self.request, "资产已更新。")
        return response


class BorrowRecordListView(LoginRequiredMixin, ListView):
    model = BorrowRecord
    template_name = "assets/borrow_list.html"
    context_object_name = "records"

    def get_queryset(self):
        queryset = BorrowRecord.objects.select_related("asset", "borrower", "department").all()
        return scope_borrow_records(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class BorrowRecordCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = BorrowRecord
    form_class = BorrowRecordForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:borrow_list")
    extra_context = {"page_title": "登记资产领用"}

    def form_valid(self, form):
        if not is_admin(self.request.user):
            form.instance.department = get_user_department(self.request.user)
        response = super().form_valid(form)
        borrow_asset(record=self.object, operator=self.request.user, request=self.request)
        messages.success(self.request, "领用记录已登记。")
        return response


class BorrowRecordReturnView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, View):
    def post(self, request, pk):
        record = get_object_or_404(
            scope_borrow_records(BorrowRecord.objects.select_related("asset", "borrower"), request.user),
            pk=pk,
        )
        form = ReturnBorrowRecordForm(request.POST, instance=record, user=request.user)
        if form.is_valid():
            form.save()
            return_asset(record=record, operator=request.user, request=request)
            messages.success(request, "归还已登记。")
        else:
            messages.error(request, "归还登记失败，请检查输入。")
        return redirect("assets:borrow_list")


class TransferRecordListView(LoginRequiredMixin, ListView):
    model = TransferRecord
    template_name = "assets/transfer_list.html"
    context_object_name = "records"

    def get_queryset(self):
        queryset = TransferRecord.objects.select_related(
            "asset", "from_department", "to_department", "from_user", "to_user", "handled_by"
        ).all()
        return scope_transfer_records(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class TransferRecordCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = TransferRecord
    form_class = TransferRecordForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:transfer_list")
    extra_context = {"page_title": "登记资产调拨"}

    def form_valid(self, form):
        if not is_admin(self.request.user):
            department = get_user_department(self.request.user)
            form.instance.from_department = department
            form.instance.handled_by = self.request.user
        response = super().form_valid(form)
        transfer_asset(record=self.object, operator=self.request.user, request=self.request)
        messages.success(self.request, "调拨记录已登记。")
        return response


class MaintenanceRecordListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = "assets/maintenance_list.html"
    context_object_name = "records"

    def get_queryset(self):
        queryset = MaintenanceRecord.objects.select_related("asset", "reported_by").all()
        return scope_maintenance_records(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class MaintenanceRecordCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:maintenance_list")
    extra_context = {"page_title": "登记资产维修"}

    def form_valid(self, form):
        response = super().form_valid(form)
        maintain_asset(record=self.object, operator=self.request.user, request=self.request)
        messages.success(self.request, "维修记录已登记。")
        return response


class ScrapRecordListView(LoginRequiredMixin, ListView):
    model = ScrapRecord
    template_name = "assets/scrap_list.html"
    context_object_name = "records"

    def get_queryset(self):
        queryset = ScrapRecord.objects.select_related("asset", "applicant", "approved_by").all()
        return scope_scrap_records(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = is_asset_manager(self.request.user)
        return context


class ScrapRecordCreateView(LoginRequiredMixin, DepartmentScopedManagerRequiredMixin, ScopedFormMixin, CreateView):
    model = ScrapRecord
    form_class = ScrapRecordForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:scrap_list")
    extra_context = {"page_title": "登记资产报废"}

    def form_valid(self, form):
        response = super().form_valid(form)
        scrap_asset(record=self.object, operator=self.request.user, request=self.request)
        messages.success(self.request, "报废记录已登记。")
        return response


class OperationLogListView(LoginRequiredMixin, ListView):
    model = OperationLog
    template_name = "assets/operation_log_list.html"
    context_object_name = "logs"
    paginate_by = 20

    def get_queryset(self):
        queryset = OperationLog.objects.select_related("user").all()
        return scope_operation_logs(queryset, self.request.user)
