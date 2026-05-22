from rest_framework.permissions import SAFE_METHODS, BasePermission

from .access import is_admin, is_asset_manager


class ScopedAssetPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_admin(user) or is_asset_manager(user)
