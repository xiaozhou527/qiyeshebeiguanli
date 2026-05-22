from dataclasses import dataclass

from django.contrib.auth.models import Group

from .constants import ADMIN_GROUP, ASSET_MANAGER_GROUP, EMPLOYEE_GROUP
from .extensions import extension_registry
from .models import OperationLog


@dataclass
class RequestMeta:
    ip_address: str | None = None


def build_request_meta(request):
    if request is None:
        return RequestMeta()
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    return RequestMeta(ip_address=ip_address)


def log_operation(
    *,
    user,
    action,
    target_type,
    target_id="",
    target_label="",
    message="",
    detail=None,
    request_meta=None,
):
    request_meta = request_meta or RequestMeta()
    log = OperationLog.objects.create(
        user=user,
        action=action,
        target_type=target_type,
        target_id=str(target_id or ""),
        target_label=target_label,
        message=message,
        detail=detail or {},
        ip_address=request_meta.ip_address,
    )
    extension_registry.dispatch(
        "operation.logged",
        {
            "log_id": log.pk,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
        },
    )
    return log


def ensure_default_groups():
    for name in (ADMIN_GROUP, ASSET_MANAGER_GROUP, EMPLOYEE_GROUP):
        Group.objects.get_or_create(name=name)
