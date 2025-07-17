from decimal import Decimal

from pydantic import BaseModel


class PlotGenerationData(BaseModel):
    label: str
    color: str
    theme: str
    sub_theme: str
    topic: str
    date_from: str
    date_to: str
    age: str
    sex: str
    stratum: str
    geography_type: str
    geograpy: str



class SubplotChartSubplotData(BaseModel):
    """Holds all the information needed to draw an individual chart / subplot"""
    subplot_title: str
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



