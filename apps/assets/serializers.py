from rest_framework import serializers

from apps.core.models import Department

from .models import Asset, AssetCategory, BorrowRecord, MaintenanceRecord, ScrapRecord, TransferRecord


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "code", "name", "manager", "description", "is_active", "created_at", "updated_at"]


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = "__all__"


class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.username", read_only=True)

    class Meta:
        model = Asset
        fields = "__all__"


class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = "__all__"


class TransferRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferRecord
        fields = "__all__"


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = "__all__"


class ScrapRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapRecord
        fields = "__all__"
