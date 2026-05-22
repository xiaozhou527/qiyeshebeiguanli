from django.contrib.auth.models import Group

from .access import get_user_department
from .constants import ASSET_MANAGER_GROUP, EMPLOYEE_GROUP
from .models import OperationLog
from .services import build_request_meta, log_operation


def register_user(*, creator, user, role_name, department=None, title="", phone="", request=None):
    group = Group.objects.get(name=role_name)
    user.groups.add(group)
    if role_name == ASSET_MANAGER_GROUP:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
    profile = user.profile
    profile.department = department or get_user_department(creator)
    profile.created_by = creator
    profile.title = title
    profile.phone = phone
    profile.save()
    log_operation(
        user=creator,
        action=OperationLog.ActionType.CREATE,
        target_type="auth.user",
        target_id=user.pk,
        target_label=user.username,
        message="注册用户账号",
        detail={"role": role_name, "department": getattr(profile.department, "name", "")},
        request_meta=build_request_meta(request),
    )
    return user
