from pydantic import BaseModel

from metrics.domain.models.charts.common import BaseChartRequestParams
from metrics.domain.models.plots import PlotParameters


class StaticFields(BaseModel):
    topic: str
    metric: str
    geography: str
    geography_type: str
    age: str
    sex: str
    stratum: str
    date_from: str
    date_to: str


class DualCategoryChartRequestParams(BaseChartRequestParams):
    chart_type: str
    secondary_category: str
    primary_field_values: list[str]
    static_fields: StaticFields
    plots: list[PlotParameters]
    legend_title: str | None = ""
