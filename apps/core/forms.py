from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .access import can_register_asset_manager, can_register_employee, get_user_department
from .models import Department


class BaseRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="姓名", max_length=150, required=False)
    phone = forms.CharField(label="联系电话", max_length=32, required=False)
    title = forms.CharField(label="岗位", max_length=64, required=False)

    def __init__(self, *args, creator=None, **kwargs):
        self.creator = creator
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-control"
            if isinstance(field.widget, forms.Select):
                css_class = "form-select"
            field.widget.attrs.setdefault("class", css_class)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "password1", "password2")


class AssetManagerRegistrationForm(BaseRegistrationForm):
    department = forms.ModelChoiceField(label="所属部门", queryset=Department.objects.none())

    def __init__(self, *args, creator=None, **kwargs):
        super().__init__(*args, creator=creator, **kwargs)
        self.fields["title"].initial = "资产管理员"
        self.fields["department"].queryset = Department.objects.filter(is_active=True).order_by("code")

    def clean(self):
        cleaned_data = super().clean()
        if not can_register_asset_manager(self.creator):
            raise forms.ValidationError("当前账号无权注册资产管理员。")
        return cleaned_data


class EmployeeRegistrationForm(BaseRegistrationForm):
    department = forms.CharField(label="所属部门", required=False, disabled=True)

    def __init__(self, *args, creator=None, **kwargs):
        super().__init__(*args, creator=creator, **kwargs)
        department = get_user_department(creator) if creator else None
        self.fields["title"].initial = "普通员工"
        self.fields["department"].initial = department.name if department else "未绑定部门"

    def clean(self):
        cleaned_data = super().clean()
        if not can_register_employee(self.creator):
            raise forms.ValidationError("当前账号无权注册普通员工。")
        if not get_user_department(self.creator):
            raise forms.ValidationError("资产管理员必须先绑定所属部门后才能注册员工。")
        return cleaned_data
