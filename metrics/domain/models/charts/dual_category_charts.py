from collections.abc import Iterable
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel
from rest_framework.request import Request

from metrics.domain.models.charts.segments import SegmentParameters


class StaticFields(BaseModel):
    theme: str
    sub_theme: str
    topic: str
    metric: str
    geography: str
    geography_type: str
    age: str
    sex: str
    stratum: str
    date_from: str
    date_to: str


class DualCategoryChartRequestParams(BaseModel):
    chart_type: str
    secondary_category: str
    static_fields: StaticFields
    segments: list[SegmentParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]
    chart_width: int
    chart_height: int
    x_axis: str
    x_axis_title: str
    y_axis: str
    y_axis_title: str
    y_axis_minimum_value: Decimal | int = 0
    y_axis_maximum_value: Decimal | int | None = None
    request: Request | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])
