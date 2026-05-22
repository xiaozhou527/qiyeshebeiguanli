from django.contrib import admin

from .models import Department, OperationLog, UserProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "manager", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "target_type", "target_label", "user")
    search_fields = ("target_type", "target_label", "message")
    list_filter = ("action", "target_type")
    readonly_fields = (
        "created_at",
        "updated_at",
        "user",
        "action",
        "target_type",
        "target_id",
        "target_label",
        "message",
        "detail",
        "ip_address",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "created_by", "title", "phone", "created_at")
    search_fields = ("user__username", "department__name", "title", "phone", "created_by__username")
    list_filter = ("department",)

# Register your models here.
