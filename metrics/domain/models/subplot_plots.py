from decimal import Decimal

from pydantic import BaseModel

from metrics.domain.models.plots import PlotGenerationData


class SubplotGenerationData(BaseModel):
    subplot_title: str
    subplot_data: list[PlotGenerationData]


class SubplotChartGenerationPayload(BaseModel):
    """Holds all the request information / params for a `Subplot Chart` in its entirety."""

    subplot_data: list[SubplotGenerationData]
    chart_width: int
    chart_height: int
    x_axis_title: str
    y_axis_title: str
    y_axis_minimum_value: Decimal = 0
    y_axis_maximum_value: Decimal | None = None
