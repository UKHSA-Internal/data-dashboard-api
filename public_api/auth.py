from rest_framework.request import Request

from common.auth.permissions import PermissionSetsType


def is_authenticated_request(request: Request) -> bool:
    """Return whether successfully authenticated the request credentials."""
    return getattr(request, "auth", None) is not None


def get_permission_sets_for_request(
    request: Request,
) -> PermissionSetsType | None:
    """Return permissions only when the request has authenticated credentials"""
    if not is_authenticated_request(request):
        return None

    request_user = getattr(request, "user", None)
    return getattr(request_user, "permission_sets", None)
