from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        on_delete=models.CASCADE,
        related_name="chat_sessions",
    )
    title = models.CharField("会话标题", max_length=128, default="新对话")

    class Meta:
        verbose_name = "对话会话"
        verbose_name_plural = "对话会话"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(TimeStampedModel):
    class Role(models.TextChoices):
        USER = "user", "用户"
        ASSISTANT = "assistant", "助手"
        SYSTEM = "system", "系统"

    session = models.ForeignKey(
        ChatSession,
        verbose_name="所属会话",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField("角色", max_length=16, choices=Role.choices)
    content = models.TextField("内容")

    class Meta:
        verbose_name = "对话消息"
        verbose_name_plural = "对话消息"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_role_display()} - {self.content[:40]}"


class AIConfig(models.Model):
    """AI 助手配置（单例）。"""

    api_key = models.CharField("API Key", max_length=255, blank=True, default="")
    base_url = models.CharField(
        "API Base URL", max_length=255, default="https://api.deepseek.com"
    )
    model = models.CharField("模型名称", max_length=64, default="deepseek-chat")

    class Meta:
        verbose_name = "AI 配置"
        verbose_name_plural = "AI 配置"

    def __str__(self):
        return "AI 配置"

    @classmethod
    def get_solo(cls):
        """返回唯一的配置实例，不存在时用 settings 中的环境变量值创建。"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
                "model": settings.DEEPSEEK_MODEL,
            },
        )
        return obj
