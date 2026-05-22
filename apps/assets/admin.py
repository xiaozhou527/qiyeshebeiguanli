from django.contrib import admin

from .models import Asset, AssetCategory, BorrowRecord, MaintenanceRecord, ScrapRecord, TransferRecord


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "parent", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "department", "assignee", "status")
    search_fields = ("code", "name", "brand", "model")
    list_filter = ("status", "category", "department")


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ("asset", "borrower", "department", "status", "borrowed_at", "returned_at")
    list_filter = ("status", "department")
    search_fields = ("asset__code", "asset__name", "borrower__username")


@admin.register(TransferRecord)
class TransferRecordAdmin(admin.ModelAdmin):
    list_display = ("asset", "from_department", "to_department", "to_user", "transferred_at")
    list_filter = ("from_department", "to_department")
    search_fields = ("asset__code", "asset__name")


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("asset", "status", "maintenance_vendor", "maintainer", "started_at", "completed_at")
    list_filter = ("status",)
    search_fields = ("asset__code", "asset__name", "maintenance_vendor")


@admin.register(ScrapRecord)
class ScrapRecordAdmin(admin.ModelAdmin):
    list_display = ("asset", "applicant", "approval_status", "requested_at", "approved_at")
    list_filter = ("approval_status",)
    search_fields = ("asset__code", "asset__name", "applicant__username")

# Register your models here.
