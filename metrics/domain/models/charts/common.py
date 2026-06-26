from decimal import Decimal
from typing import Literal

from metrics.domain.models.common import BaseRequestParams


class ChartBaseRequestParams(BaseRequestParams):
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
    confidence_intervals: bool | None = False
    confidence_colour: str | None = ""
    is_public: bool | None = True
    data_classification: str | None = None
