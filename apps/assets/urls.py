from django.urls import path

from . import views

app_name = "assets"

urlpatterns = [
    path("departments/", views.DepartmentListView.as_view(), name="department_list"),
    path("departments/create/", views.DepartmentCreateView.as_view(), name="department_create"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("assets/", views.AssetListView.as_view(), name="asset_list"),
    path("assets/create/", views.AssetCreateView.as_view(), name="asset_create"),
    path("assets/<int:pk>/", views.AssetDetailView.as_view(), name="asset_detail"),
    path("assets/<int:pk>/edit/", views.AssetUpdateView.as_view(), name="asset_edit"),
    path("borrow-records/", views.BorrowRecordListView.as_view(), name="borrow_list"),
    path("borrow-records/create/", views.BorrowRecordCreateView.as_view(), name="borrow_create"),
    path("borrow-records/<int:pk>/return/", views.BorrowRecordReturnView.as_view(), name="borrow_return"),
    path("transfers/", views.TransferRecordListView.as_view(), name="transfer_list"),
    path("transfers/create/", views.TransferRecordCreateView.as_view(), name="transfer_create"),
    path("maintenances/", views.MaintenanceRecordListView.as_view(), name="maintenance_list"),
    path("maintenances/create/", views.MaintenanceRecordCreateView.as_view(), name="maintenance_create"),
    path("scraps/", views.ScrapRecordListView.as_view(), name="scrap_list"),
    path("scraps/create/", views.ScrapRecordCreateView.as_view(), name="scrap_create"),
    path("logs/", views.OperationLogListView.as_view(), name="operation_log_list"),
]
