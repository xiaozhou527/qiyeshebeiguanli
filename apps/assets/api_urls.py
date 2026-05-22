from rest_framework.routers import DefaultRouter

from .api import (
    AssetCategoryViewSet,
    AssetViewSet,
    BorrowRecordViewSet,
    DepartmentViewSet,
    MaintenanceRecordViewSet,
    ScrapRecordViewSet,
    TransferRecordViewSet,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("categories", AssetCategoryViewSet, basename="category")
router.register("assets", AssetViewSet, basename="asset")
router.register("borrow-records", BorrowRecordViewSet, basename="borrow-record")
router.register("transfer-records", TransferRecordViewSet, basename="transfer-record")
router.register("maintenance-records", MaintenanceRecordViewSet, basename="maintenance-record")
router.register("scrap-records", ScrapRecordViewSet, basename="scrap-record")

urlpatterns = router.urls
