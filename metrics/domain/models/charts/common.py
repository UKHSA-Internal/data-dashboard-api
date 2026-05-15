from collections.abc import Iterable
from decimal import Decimal
from typing import Literal

from pydantic.main import BaseModel
from rest_framework.request import Request


class BaseChartRequestParams(BaseModel):
    file_format: Literal["png", "svg", "jpg", "jpeg", "json", "csv"]
    chart_width: int
    chart_height: int
    x_axis: str
    x_axis_title: str = ""
    y_axis: str
    y_axis_title: str = ""
    y_axis_minimum_value: Decimal | int = 0
    y_axis_maximum_value: Decimal | int | None = None
    legend_title: str | None = ""
    request: Request | None = None
    confidence_intervals: bool | None = False
    confidence_colour: str | None = ""

    class Config:
        arbitrary_types_allowed = True

    # LEGACY PERMISSIONS (NOT IN USE): RBAC-based permissions will be removed in a future release
    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])

    @property
    def jwt_permissions(self) -> dict:
        """Extract JWT permissions from the authenticated request.

        Returns a dict with:
        - 'has_global_access' (bool): Whether user has access to all data
        - 'permission_set_hierarchy' (list): User's permission hierarchy from JWT

        Returns empty dict if not authenticated or no permissions available.
        """
        if self.request is None:
            return {}

        user = getattr(self.request, "user", None)
        if user is None:
            return {}

        permission_sets = getattr(user, "permission_sets", {})
        if not permission_sets:
            return {}

        return permission_sets


