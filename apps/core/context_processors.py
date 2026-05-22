from .access import can_manage_users, can_register_asset_manager, can_register_employee


def system_context(request):
    return {
        "system_name": "企业资产管理系统",
        "can_manage_users": can_manage_users(getattr(request, "user", None)),
        "can_register_asset_manager": can_register_asset_manager(getattr(request, "user", None)),
        "can_register_employee": can_register_employee(getattr(request, "user", None)),
    }
