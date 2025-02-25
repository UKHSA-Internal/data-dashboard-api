from enum import Enum
from functools import wraps

from django.db import Error
from django.http import JsonResponse

from config import AUTH_ENABLED
from metrics.data.models.rbac_models import RBACGroupPermission

RBAC_AUTH_X_HEADER = "X-GroupId"


class ErrorCode(Enum):
    INVALID_GROUP_ID = 1115


def authorised_route(func):
    @wraps(func)
    def wrap(self, request, *args, **kwargs):
        if not AUTH_ENABLED:
            return func(self, request, *args, **kwargs)
        try:
            if RBAC_AUTH_X_HEADER in request.headers:
                group_id = request.headers.get(RBAC_AUTH_X_HEADER)
                if group_id == "":
                    raise InvalidGroupIdError
                _set_rbac_group_permissions(request, group_id)
        except InvalidGroupIdError:
            return JsonResponse(
                {"error": "Access Denied", "code": ErrorCode.INVALID_GROUP_ID.value},
                status=403,
            )
        return func(self, request, *args, **kwargs)

    return wrap


def _set_rbac_group_permissions(request, group_id: str) -> None:
    try:
        group_permissions = RBACGroupPermission.objects.get_group(name=group_id)
        if group_permissions:
            request.group_permissions = list(group_permissions.permissions.all())
        else:
            raise InvalidGroupIdError
    except Error:
        """Catch all for database related errors"""
        raise InvalidGroupIdError


class InvalidGroupIdError(Exception):
    """Custom exception for invalid RBAC group ID"""
