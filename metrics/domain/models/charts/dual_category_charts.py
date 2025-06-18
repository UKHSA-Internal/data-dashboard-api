from pydantic import BaseModel

from metrics.domain.models.charts.common import BaseChartRequestParams
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


class DualCategoryChartRequestParams(BaseChartRequestParams):
    chart_type: str
    secondary_category: str
    static_fields: StaticFields
    segments: list[SegmentParameters]
