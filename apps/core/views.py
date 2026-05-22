from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from .access import (
    can_manage_users,
    can_register_asset_manager,
    can_register_employee,
    is_admin,
    scope_users,
)
from .constants import ASSET_MANAGER_GROUP, EMPLOYEE_GROUP
from .forms import AssetManagerRegistrationForm, EmployeeRegistrationForm
from .user_services import register_user


class UserManagementRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage_users(self.request.user)


class UserListView(UserManagementRequiredMixin, ListView):
    model = get_user_model()
    template_name = "core/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = (
            get_user_model()
            .objects.select_related("profile", "profile__department", "profile__created_by")
            .prefetch_related("groups")
            .order_by("username")
        )
        return scope_users(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_register_asset_manager"] = can_register_asset_manager(self.request.user)
        context["can_register_employee"] = can_register_employee(self.request.user)
        context["managed_role_label"] = "资产管理员" if is_admin(self.request.user) else "普通员工"
        return context


class AssetManagerRegisterView(UserManagementRequiredMixin, FormView):
    template_name = "core/register_user.html"
    form_class = AssetManagerRegistrationForm
    success_url = reverse_lazy("core:user_list")

    def dispatch(self, request, *args, **kwargs):
        if not can_register_asset_manager(request.user):
            messages.error(request, "只有管理员可以注册资产管理员账号。")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["creator"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "注册资产管理员"
        context["target_role"] = "资产管理员"
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.first_name = form.cleaned_data["first_name"]
        user.save()
        register_user(
            creator=self.request.user,
            user=user,
            role_name=ASSET_MANAGER_GROUP,
            department=form.cleaned_data["department"],
            title=form.cleaned_data["title"] or "资产管理员",
            phone=form.cleaned_data["phone"],
            request=self.request,
        )
        messages.success(self.request, "资产管理员账号已创建。")
        return super().form_valid(form)


class EmployeeRegisterView(UserManagementRequiredMixin, FormView):
    template_name = "core/register_user.html"
    form_class = EmployeeRegistrationForm
    success_url = reverse_lazy("core:user_list")

    def dispatch(self, request, *args, **kwargs):
        if not can_register_employee(request.user):
            messages.error(request, "只有资产管理员可以注册普通员工账号。")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["creator"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "注册普通员工"
        context["target_role"] = "普通员工"
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.first_name = form.cleaned_data["first_name"]
        user.save()
        register_user(
            creator=self.request.user,
            user=user,
            role_name=EMPLOYEE_GROUP,
            title=form.cleaned_data["title"] or "普通员工",
            phone=form.cleaned_data["phone"],
            request=self.request,
        )
        messages.success(self.request, "普通员工账号已创建。")
        return super().form_valid(form)
