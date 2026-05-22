from django.urls import path

from .views import AssetManagerRegisterView, EmployeeRegisterView, UserListView

app_name = "core"

urlpatterns = [
    path("accounts/users/", UserListView.as_view(), name="user_list"),
    path("accounts/register/asset-manager/", AssetManagerRegisterView.as_view(), name="register_asset_manager"),
    path("accounts/register/employee/", EmployeeRegisterView.as_view(), name="register_employee"),
]
