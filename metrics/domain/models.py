from typing import List, Literal, Optional

from pydantic.main import BaseModel


class ChartsPlotParameters(BaseModel):
    chart_type: str
    topic: str
    metric: str
    stratum: Optional[str]
    geography: Optional[str]
    geography_type: Optional[str]
    date_from: Optional[str]
    date_to: Optional[str]


class ChartPlots(BaseModel):
    plots: List[ChartsPlotParameters]
    file_format: Literal["png", "svg", "jpg", "jpeg"]
