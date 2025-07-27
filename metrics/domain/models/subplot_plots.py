from typing import Any
from decimal import Decimal

from pydantic import BaseModel


class PlotGenerationData(BaseModel):
    parameters: dict[str, str]
    x_axis_values: Any
    y_axis_values: Any
    latest_date: Any = None


class SubplotChartSubplotData(BaseModel):
    """Holds all the information needed to draw an individual chart / subplot"""
    subplot_title: str
    subplot_parameters: dict[str, str]
    plots: list[PlotGenerationData]


class SubplotChartRequestParams(BaseModel):
    """Holds all the request information / params for a `Subplot Chart` in its entirety."""

    subplot_data: list[SubplotChartSubplotData]
    chart_width: int
    chart_height: int
    x_axis_title: str
    y_axis_title: str
    y_axis_minimum_value: Decimal = 0
    y_axis_maximum_value: Decimal | None = None
