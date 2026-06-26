from collections.abc import Iterable

from pydantic.main import BaseModel
from rest_framework.request import Request

from common.auth.permissions import PermissionSetsType


class BaseRequestParams(BaseModel):
    request: Request | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def permission_sets(self) -> PermissionSetsType:
        """Extract optional JWT permissions from the authenticated request"""

        request_user = getattr(self.request, "user", None)
        return getattr(request_user, "permission_sets", {})

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])
