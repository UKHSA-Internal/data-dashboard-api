from rest_framework.request import Request

from common.auth.permissions import PermissionSetsType
from public_api.metrics_interface.interface import MetricsPublicAPIInterface


def is_authenticated_request(request: Request) -> bool:
    """Return whether authenticated public API access is enabled for the request."""
    return (
        MetricsPublicAPIInterface.is_auth_enabled()
        and getattr(request, "auth", None) is not None
    )


def get_permission_sets_for_request(
    request: Request,
) -> PermissionSetsType | None:
    """Return permissions only when authenticated public API access is enabled"""
    if not is_authenticated_request(request):
        return None

    request_user = getattr(request, "user", None)
    return getattr(request_user, "permission_sets", None)
