import datetime
from decimal import Decimal
from typing import Literal

from pydantic.main import BaseModel
from rest_framework.request import Request

OPTIONAL_STRING = str | None


class SubplotChartSubplotsPlotsParameters(BaseModel):
    label: str
    colour: str
    age: OPTIONAL_STRING = ""
    sex: OPTIONAL_STRING = ""
    stratum: OPTIONAL_STRING = ""
    geography_type: OPTIONAL_STRING = ""
    geography: OPTIONAL_STRING = ""


class SubplotChartSubplotsParameters(BaseModel):
    metric: str
    topic: str
    stratum: str


class SubplotChartSubplots(BaseModel):
    subplot_title: str
    subplot_parameters: SubplotChartSubplotsParameters
    plots: list[SubplotChartSubplotsPlotsParameters]


class SubplotChartParameters(BaseModel):
    theme: str
    sub_theme: str
    date_from: datetime.date
    date_to: datetime.date
    age: OPTIONAL_STRING = ""
    sex: OPTIONAL_STRING = ""
    stratum: OPTIONAL_STRING = ""
    geography_type: OPTIONAL_STRING = ""
    geography: OPTIONAL_STRING = ""


class SubplotChartRequestParameters(BaseModel):
    file_format: Literal["png", "svg", "jpg", "jpeg"]
    chart_width: int
    chart_height: int
    x_axis_title: OPTIONAL_STRING = ""
    y_axis_title: OPTIONAL_STRING = ""
    y_axis_minimum_value: Decimal | int | None = 0
    y_axis_maximum_value: Decimal | int | None = None

    chart_parameters: SubplotChartParameters
    subplots: list[SubplotChartSubplots]

    request: Request | None = None

    class Config:
        arbitrary_types_allowed = True
