import logging
from collections.abc import Iterable
from decimal import Decimal
from typing import Literal

from pydantic.main import BaseModel
from rest_framework.request import Request

logger = logging.getLogger(__name__)


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

    @property
    def permission_sets(self) -> dict:
        """Extract JWT permissions from the authenticated request"""

        logger.info("Entered BaseChartRequestParams.permission_sets")

        return getattr(self.request.user, "permission_sets", {})

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        """TODO: RBAC-based permissions are legacy and will be removed in a future release"""

        return getattr(self.request, "rbac_permissions", [])
