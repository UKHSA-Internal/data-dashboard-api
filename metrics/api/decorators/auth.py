from functools import wraps

from django.core.exceptions import ValidationError
from django.http import HttpRequest

from metrics.api.settings.private_api import AUTH_ENABLED
from metrics.data.models.rbac_models import RBACGroupPermission

RBAC_AUTH_X_HEADER = "X-GroupId"


def require_authorisation(func):
    @wraps(func)
    def wrap(self, request, *args, **kwargs):
        if not AUTH_ENABLED:
            return func(self, request, *args, **kwargs)
        try:
            group_id: str = request.headers[RBAC_AUTH_X_HEADER]
        except KeyError:
            pass
        else:
            _set_rbac_group_permissions(request=request, group_id=group_id)
        return func(self, request, *args, **kwargs)

    return wrap


def _set_rbac_group_permissions(*, request: HttpRequest, group_id: str) -> None:
    request.group_permissions = []
    if not group_id:
        return

    try:
        group_permissions: RBACGroupPermission = RBACGroupPermission.objects.get_group(
            group_id=group_id
        )
    except ValidationError:
        return

    if group_permissions:
        request.group_permissions = list(group_permissions.permissions.all())
