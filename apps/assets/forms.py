from django import forms
from django.contrib.auth import get_user_model

from apps.core.access import get_user_department, is_admin, is_asset_manager
from apps.core.models import Department

from .models import Asset, AssetCategory, BorrowRecord, MaintenanceRecord, ScrapRecord, TransferRecord


class DateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class DateInput(forms.DateInput):
    input_type = "date"


class BaseStyledModelForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.apply_scope()
        for field in self.fields.values():
            css_class = "form-control"
            if isinstance(field.widget, forms.Select):
                css_class = "form-select"
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            field.widget.attrs.setdefault("class", css_class)

    def apply_scope(self):
        return None


class DepartmentForm(BaseStyledModelForm):
    def apply_scope(self):
        if not self.user or is_admin(self.user):
            return
        department = get_user_department(self.user)
        self.fields["manager"].queryset = get_user_model().objects.filter(
            profile__department=department
        )

    class Meta:
        model = Department
        fields = ["code", "name", "manager", "description", "is_active"]


class AssetCategoryForm(BaseStyledModelForm):
    class Meta:
        model = AssetCategory
        fields = ["code", "name", "parent", "description", "is_active"]


class AssetForm(BaseStyledModelForm):
    def apply_scope(self):
        if not self.user or is_admin(self.user):
            return
        if is_asset_manager(self.user):
            department = get_user_department(self.user)
            department_id = getattr(department, "id", None)
            self.fields["department"].queryset = Department.objects.filter(id=department_id)
            self.fields["assignee"].queryset = get_user_model().objects.filter(
                profile__department_id=department_id
            )

    class Meta:
        model = Asset
        fields = [
            "code",
            "name",
            "category",
            "brand",
            "model",
            "specification",
            "purchase_date",
            "purchase_price",
            "department",
            "assignee",
            "location",
            "status",
            "remarks",
        ]
        widgets = {
            "purchase_date": DateInput(),
        }


class BorrowRecordForm(BaseStyledModelForm):
    def apply_scope(self):
        if not self.user or is_admin(self.user):
            return
        if is_asset_manager(self.user):
            department_id = getattr(get_user_department(self.user), "id", None)
            self.fields["asset"].queryset = Asset.objects.filter(department_id=department_id)
            self.fields["department"].queryset = Department.objects.filter(id=department_id)
            self.fields["borrower"].queryset = get_user_model().objects.filter(
                profile__department_id=department_id
            )

    class Meta:
        model = BorrowRecord
        fields = [
            "asset",
            "borrower",
            "department",
            "purpose",
            "borrowed_at",
            "expected_return_at",
            "note",
        ]
        widgets = {
            "borrowed_at": DateTimeInput(),
            "expected_return_at": DateTimeInput(),
        }


class ReturnBorrowRecordForm(BaseStyledModelForm):
    class Meta:
        model = BorrowRecord
        fields = ["returned_at", "note"]
        widgets = {
            "returned_at": DateTimeInput(),
        }


class TransferRecordForm(BaseStyledModelForm):
    def apply_scope(self):
        if not self.user or is_admin(self.user):
            return
        if is_asset_manager(self.user):
            department_id = getattr(get_user_department(self.user), "id", None)
            self.fields["asset"].queryset = Asset.objects.filter(department_id=department_id)
            self.fields["from_department"].queryset = Department.objects.filter(id=department_id)
            self.fields["from_user"].queryset = get_user_model().objects.filter(
                profile__department_id=department_id
            )

    class Meta:
        model = TransferRecord
        fields = [
            "asset",
            "from_department",
            "to_department",
            "from_user",
            "to_user",
            "transferred_at",
            "reason",
            "handled_by",
            "note",
        ]
        widgets = {
            "transferred_at": DateTimeInput(),
        }


class MaintenanceRecordForm(BaseStyledModelForm):
    def apply_scope(self):
        if not self.user or is_admin(self.user):
            return
        if is_asset_manager(self.user):
            department_id = getattr(get_user_department(self.user), "id", None)
            self.fields["asset"].queryset = Asset.objects.filter(department_id=department_id)
            self.fields["reported_by"].queryset = get_user_model().objects.filter(
                profile__department_id=department_id
            )

    class Meta:
        model = MaintenanceRecord
        fields = [
            "asset",
            "reported_by",
            "issue_description",
            "maintenance_vendor",
            "maintainer",
            "started_at",
            "completed_at",
            "result",
            "cost",
            "status",
        ]
        widgets = {
            "started_at": DateTimeInput(),
            "completed_at": DateTimeInput(),
        }


class ScrapRecordForm(BaseStyledModelForm):
    def apply_scope(self):
        if not self.user or is_admin(self.user):
            return
        if is_asset_manager(self.user):
            department_id = getattr(get_user_department(self.user), "id", None)
            department_users = get_user_model().objects.filter(
                profile__department_id=department_id
            )
            self.fields["asset"].queryset = Asset.objects.filter(department_id=department_id)
            self.fields["applicant"].queryset = department_users
            self.fields["approved_by"].queryset = department_users

    class Meta:
        model = ScrapRecord
        fields = [
            "asset",
            "applicant",
            "requested_at",
            "reason",
            "approval_status",
            "approved_by",
            "approved_at",
            "disposal_note",
        ]
        widgets = {
            "requested_at": DateTimeInput(),
            "approved_at": DateTimeInput(),
        }
