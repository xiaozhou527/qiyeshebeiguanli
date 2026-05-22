from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True


class Department(TimeStampedModel):
    code = models.CharField("部门编码", max_length=32, unique=True)
    name = models.CharField("部门名称", max_length=64, unique=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="负责人",
        on_delete=models.SET_NULL,
        related_name="managed_departments",
        null=True,
        blank=True,
    )
    description = models.TextField("描述", blank=True)
    is_active = models.BooleanField("启用", default=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    department = models.ForeignKey(
        Department,
        verbose_name="所属部门",
        on_delete=models.SET_NULL,
        related_name="members",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="创建人",
        on_delete=models.SET_NULL,
        related_name="created_user_profiles",
        null=True,
        blank=True,
    )
    phone = models.CharField("联系电话", max_length=32, blank=True)
    title = models.CharField("岗位", max_length=64, blank=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "用户档案"
        verbose_name_plural = "用户档案"
        ordering = ["user__username"]

    def __str__(self):
        department_name = self.department.name if self.department else "未分配部门"
        return f"{self.user.username} - {department_name}"


class OperationLog(TimeStampedModel):
    class ActionType(models.TextChoices):
        CREATE = "create", "新增"
        UPDATE = "update", "修改"
        DELETE = "delete", "删除"
        LOGIN = "login", "登录"
        LOGOUT = "logout", "登出"
        BUSINESS = "business", "业务操作"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="操作人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField("动作", max_length=32, choices=ActionType.choices)
    target_type = models.CharField("对象类型", max_length=64)
    target_id = models.CharField("对象ID", max_length=64, blank=True)
    target_label = models.CharField("对象名称", max_length=255, blank=True)
    message = models.CharField("摘要", max_length=255)
    detail = models.JSONField("详细信息", default=dict, blank=True)
    ip_address = models.GenericIPAddressField("IP地址", null=True, blank=True)

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = "操作日志"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} - {self.message}"
