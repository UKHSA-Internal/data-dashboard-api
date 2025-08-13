from collections.abc import Iterable
from decimal import Decimal
from typing import Literal

from pydantic.main import BaseModel
from rest_framework.request import Request

from metrics.domain.models.plots import PlotParameters

OPTIONAL_STRING = str | None


class Subplots(BaseModel):
    subplot_title: str
    x_axis: str
    y_axis: str
    plots: list[PlotParameters]
    request: Request | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])


"""
This collection of models are the model definitions for a `Request` for a subplot chart.
"""


class SubplotChartRequestParameters(BaseModel):
    file_format: Literal["png", "svg", "jpg", "jpeg"]
    chart_width: int
    chart_height: int
    x_axis_title: OPTIONAL_STRING = ""
    y_axis_title: OPTIONAL_STRING = ""
    y_axis_minimum_value: Decimal | int | None = 0
    y_axis_maximum_value: Decimal | int | None = None
    target_threshold: float | None = None
    request: Request | None = None

    subplots: list[Subplots]

    class Config:
        arbitrary_types_allowed = True
