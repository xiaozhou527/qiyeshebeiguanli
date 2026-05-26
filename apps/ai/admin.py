from django.contrib import admin
from django import forms

from .models import AIConfig, ChatMessage, ChatSession


class AIConfigForm(forms.ModelForm):
    api_key = forms.CharField(
        label="API Key",
        max_length=255,
        required=False,
        widget=forms.PasswordInput(render_value=True),
    )

    class Meta:
        model = AIConfig
        fields = "__all__"


@admin.register(AIConfig)
class AIConfigAdmin(admin.ModelAdmin):
    form = AIConfigForm
    fieldsets = (
        (None, {"fields": ("api_key", "base_url", "model")}),
    )

    def has_add_permission(self, request):
        return not AIConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "created_at", "updated_at")
    search_fields = ("title", "user__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "content", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)
    readonly_fields = ("created_at", "updated_at")
