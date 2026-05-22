from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import OperationLog
from .services import build_request_meta, log_operation


class OperationLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    meta = build_request_meta(request)
    log_operation(
        user=user,
        action=OperationLog.ActionType.LOGIN,
        target_type="auth.user",
        target_id=user.pk,
        target_label=user.get_username(),
        message="用户登录系统",
        detail={},
        request_meta=meta,
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    if user is None:
        return
    meta = build_request_meta(request)
    log_operation(
        user=user,
        action=OperationLog.ActionType.LOGOUT,
        target_type="auth.user",
        target_id=user.pk,
        target_label=user.get_username(),
        message="用户退出系统",
        detail={},
        request_meta=meta,
    )
