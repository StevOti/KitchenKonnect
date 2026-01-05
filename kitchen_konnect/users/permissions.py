from functools import wraps

from rest_framework.permissions import BasePermission


class IsNutritionist(BasePermission):
    """Allow access only to users with role 'nutritionist'."""

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'nutritionist')


class IsRegulator(BasePermission):
    """Allow access only to users with role 'regulator'."""

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'regulator')


class IsAdminRole(BasePermission):
    """Allow access only to users with role 'admin'."""

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'admin')


class IsAdminLevel(BasePermission):
    """Allow access to users with admin_level >= view.min_admin_level.

    The view should define an integer attribute `min_admin_level` (default 1).
    """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            return False
        try:
            user_level = int(getattr(user, 'admin_level', 0) or 0)
        except Exception:
            user_level = 0
        min_level = getattr(view, 'min_admin_level', 1)
        try:
            min_level = int(min_level)
        except Exception:
            min_level = 1
        return user_level >= min_level


def role_required(role):
    """View decorator for Django views (non-DRF) that ensures request.user has `role`.

    Usage:
        @role_required('nutritionist')
        def my_view(request):
            ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not (user and user.is_authenticated and getattr(user, 'role', '') == role):
                from django.http import HttpResponseForbidden

                return HttpResponseForbidden('Forbidden')
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
