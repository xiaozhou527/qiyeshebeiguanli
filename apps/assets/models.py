from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import Department, TimeStampedModel


class AssetCategory(TimeStampedModel):
    code = models.CharField("分类编码", max_length=32, unique=True)
    name = models.CharField("分类名称", max_length=64, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="上级分类",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField("描述", blank=True)
    is_active = models.BooleanField("启用", default=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "资产分类"
        verbose_name_plural = "资产分类"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Asset(TimeStampedModel):
    class Status(models.TextChoices):
        IDLE = "idle", "闲置"
        IN_USE = "in_use", "使用中"
        REPAIRING = "repairing", "维修中"
        SCRAPPED = "scrapped", "已报废"

    code = models.CharField("资产编号", max_length=64, unique=True)
    name = models.CharField("资产名称", max_length=128)
    category = models.ForeignKey(
        AssetCategory,
        verbose_name="资产分类",
        on_delete=models.PROTECT,
        related_name="assets",
    )
    brand = models.CharField("品牌", max_length=64, blank=True)
    model = models.CharField("型号", max_length=64, blank=True)
    specification = models.CharField("规格参数", max_length=255, blank=True)
    purchase_date = models.DateField("购买日期", null=True, blank=True)
    purchase_price = models.DecimalField(
        "购买价格", max_digits=12, decimal_places=2, null=True, blank=True
    )
    department = models.ForeignKey(
        Department,
        verbose_name="使用部门",
        on_delete=models.PROTECT,
        related_name="assets",
        null=True,
        blank=True,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="使用人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_assets",
    )
    location = models.CharField("存放位置", max_length=128, blank=True)
    status = models.CharField("资产状态", max_length=24, choices=Status.choices, default=Status.IDLE)
    remarks = models.TextField("备注", blank=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "资产"
        verbose_name_plural = "资产"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class BorrowRecord(TimeStampedModel):
    class Status(models.TextChoices):
        BORROWED = "borrowed", "借出中"
        RETURNED = "returned", "已归还"
        OVERDUE = "overdue", "已逾期"

    asset = models.ForeignKey(Asset, verbose_name="资产", on_delete=models.PROTECT, related_name="borrow_records")
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="领用人",
        on_delete=models.PROTECT,
        related_name="borrow_records",
    )
    department = models.ForeignKey(
        Department,
        verbose_name="领用部门",
        on_delete=models.PROTECT,
        related_name="borrow_records",
    )
    purpose = models.CharField("领用用途", max_length=255, blank=True)
    borrowed_at = models.DateTimeField("领用时间", default=timezone.now)
    expected_return_at = models.DateTimeField("预计归还时间", null=True, blank=True)
    returned_at = models.DateTimeField("实际归还时间", null=True, blank=True)
    status = models.CharField("记录状态", max_length=24, choices=Status.choices, default=Status.BORROWED)
    note = models.TextField("备注", blank=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "领用归还记录"
        verbose_name_plural = "领用归还记录"
        ordering = ["-borrowed_at"]

    def __str__(self):
        return f"{self.asset} - {self.borrower}"


class TransferRecord(TimeStampedModel):
    asset = models.ForeignKey(Asset, verbose_name="资产", on_delete=models.PROTECT, related_name="transfer_records")
    from_department = models.ForeignKey(
        Department,
        verbose_name="调出部门",
        on_delete=models.PROTECT,
        related_name="transfer_out_records",
    )
    to_department = models.ForeignKey(
        Department,
        verbose_name="调入部门",
        on_delete=models.PROTECT,
        related_name="transfer_in_records",
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="原使用人",
        on_delete=models.SET_NULL,
        related_name="transfer_out_records",
        null=True,
        blank=True,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="新使用人",
        on_delete=models.SET_NULL,
        related_name="transfer_in_records",
        null=True,
        blank=True,
    )
    transferred_at = models.DateTimeField("调拨时间", default=timezone.now)
    reason = models.CharField("调拨原因", max_length=255, blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="经办人",
        on_delete=models.SET_NULL,
        related_name="handled_transfer_records",
        null=True,
        blank=True,
    )
    note = models.TextField("备注", blank=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "资产调拨记录"
        verbose_name_plural = "资产调拨记录"
        ordering = ["-transferred_at"]

    def __str__(self):
        return f"{self.asset} - {self.from_department} -> {self.to_department}"


class MaintenanceRecord(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "待维修"
        PROCESSING = "processing", "维修中"
        DONE = "done", "已完成"

    asset = models.ForeignKey(Asset, verbose_name="资产", on_delete=models.PROTECT, related_name="maintenance_records")
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="报修人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_maintenance_records",
    )
    issue_description = models.TextField("故障描述")
    maintenance_vendor = models.CharField("维修单位", max_length=128, blank=True)
    maintainer = models.CharField("维修人员", max_length=64, blank=True)
    started_at = models.DateTimeField("开始时间", default=timezone.now)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)
    result = models.TextField("维修结果", blank=True)
    cost = models.DecimalField("维修费用", max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField("维修状态", max_length=24, choices=Status.choices, default=Status.PENDING)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "资产维修记录"
        verbose_name_plural = "资产维修记录"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.asset} - {self.get_status_display()}"


class ScrapRecord(TimeStampedModel):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "待审批"
        APPROVED = "approved", "已批准"
        REJECTED = "rejected", "已驳回"

    asset = models.ForeignKey(Asset, verbose_name="资产", on_delete=models.PROTECT, related_name="scrap_records")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="申请人",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scrap_records",
    )
    requested_at = models.DateTimeField("申请时间", default=timezone.now)
    reason = models.TextField("报废原因")
    approval_status = models.CharField(
        "审批状态",
        max_length=24,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="审批人",
        on_delete=models.SET_NULL,
        related_name="approved_scrap_records",
        null=True,
        blank=True,
    )
    approved_at = models.DateTimeField("审批时间", null=True, blank=True)
    disposal_note = models.TextField("处理说明", blank=True)
    extension_data = models.JSONField("扩展字段", default=dict, blank=True)

    class Meta:
        verbose_name = "资产报废记录"
        verbose_name_plural = "资产报废记录"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.asset} - {self.get_approval_status_display()}"

# Create your models here.
