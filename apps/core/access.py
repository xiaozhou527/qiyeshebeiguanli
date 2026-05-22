from django.db.models import Q

from .constants import ADMIN_GROUP, ASSET_MANAGER_GROUP, EMPLOYEE_GROUP


def is_admin(user):
    return bool(user) and user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists()
    )


def is_asset_manager(user):
    return bool(user) and user.is_authenticated and (
        is_admin(user) or user.groups.filter(name=ASSET_MANAGER_GROUP).exists()
    )


def is_employee(user):
    return bool(user) and user.is_authenticated and user.groups.filter(name=EMPLOYEE_GROUP).exists()


def can_register_asset_manager(user):
    return is_admin(user)


def can_register_employee(user):
    return is_asset_manager(user) and not is_admin(user)


def can_manage_users(user):
    return can_register_asset_manager(user) or can_register_employee(user)


def get_user_department(user):
    profile = getattr(user, "profile", None)
    return getattr(profile, "department", None)


def get_user_department_id(user):
    department = get_user_department(user)
    return getattr(department, "id", None)


def scope_departments(queryset, user):
    if is_admin(user):
        return queryset
    department_id = get_user_department_id(user)
    if department_id:
        return queryset.filter(id=department_id)
    return queryset.none()


def scope_assets(queryset, user):
    if is_admin(user):
        return queryset
    if is_asset_manager(user):
        department_id = get_user_department_id(user)
        return queryset.filter(department_id=department_id) if department_id else queryset.none()
    return queryset.filter(assignee=user)


def scope_borrow_records(queryset, user):
    if is_admin(user):
        return queryset
    if is_asset_manager(user):
        department_id = get_user_department_id(user)
        return queryset.filter(department_id=department_id) if department_id else queryset.none()
    return queryset.filter(borrower=user)


def scope_transfer_records(queryset, user):
    if is_admin(user):
        return queryset
    if is_asset_manager(user):
        department_id = get_user_department_id(user)
        if not department_id:
            return queryset.none()
        return queryset.filter(
            Q(from_department_id=department_id) | Q(to_department_id=department_id)
        )
    return queryset.filter(Q(from_user=user) | Q(to_user=user))


def scope_maintenance_records(queryset, user):
    if is_admin(user):
        return queryset
    if is_asset_manager(user):
        department_id = get_user_department_id(user)
        return (
            queryset.filter(asset__department_id=department_id)
            if department_id
            else queryset.none()
        )
    return queryset.filter(Q(reported_by=user) | Q(asset__assignee=user))


def scope_scrap_records(queryset, user):
    if is_admin(user):
        return queryset
    if is_asset_manager(user):
        department_id = get_user_department_id(user)
        return (
            queryset.filter(asset__department_id=department_id)
            if department_id
            else queryset.none()
        )
    return queryset.filter(Q(applicant=user) | Q(asset__assignee=user))


def scope_operation_logs(queryset, user):
    if is_admin(user):
        return queryset
    return queryset.filter(user=user)


def scope_users(queryset, user):
    if is_admin(user):
        return queryset.filter(groups__name=ASSET_MANAGER_GROUP).distinct()
    if is_asset_manager(user):
        department_id = get_user_department_id(user)
        return queryset.filter(
            groups__name=EMPLOYEE_GROUP,
            profile__department_id=department_id,
            profile__created_by=user,
        ).distinct()
    return queryset.none()
