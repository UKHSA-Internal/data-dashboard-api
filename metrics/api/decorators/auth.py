from enum import Enum
from functools import wraps

from django.db import Error
from django.http import JsonResponse

from config import AUTH_ENABLED
from metrics.data.models.rbac_models import RBACGroupPermission

RBAC_AUTH_X_HEADER = "X-GroupId"


def authorised_route(func):
    @wraps(func)
    def wrap(self, request, *args, **kwargs):
        if not AUTH_ENABLED:
            return func(self, request, *args, **kwargs)
        if RBAC_AUTH_X_HEADER in request.headers:
            group_id = request.headers.get(RBAC_AUTH_X_HEADER)
            if group_id != "":
                _set_rbac_group_permissions(request, group_id)
        return func(self, request, *args, **kwargs)
    return wrap


def _set_rbac_group_permissions(request, group_id: str) -> None:
    group_permissions = RBACGroupPermission.objects.get_group(name=group_id)
    if group_permissions:
        request.group_permissions = list(group_permissions.permissions.all())
