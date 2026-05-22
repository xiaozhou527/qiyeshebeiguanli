from django.contrib.auth.mixins import UserPassesTestMixin

from .access import get_user_department, is_admin, is_asset_manager


class AssetManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return is_asset_manager(user)


class DepartmentScopedManagerRequiredMixin(AssetManagerRequiredMixin):
    def test_func(self):
        user = self.request.user
        return is_admin(user) or bool(get_user_department(user))
