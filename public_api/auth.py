from rest_framework.request import Request

from common.auth.permissions import PermissionSetsType
from public_api.metrics_interface.interface import MetricsPublicAPIInterface


def is_authenticated_request(request: Request) -> bool:
    """Return whether authenticated public API access is enabled for the request."""
    return (
        MetricsPublicAPIInterface.is_auth_enabled()
        and request.auth
    )


def get_permission_sets_for_request(
    request: Request,
) -> PermissionSetsType | None:
    """Return permissions only when authenticated public API access is enabled"""
    if not is_authenticated_request(request):
        return None

    return getattr(request.user, "permission_sets", None)
