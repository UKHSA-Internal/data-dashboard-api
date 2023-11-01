from pydantic import BaseModel


class IncomingBaseDTO(BaseModel):
    """Base data transfer object providing common fields"""

    parent_theme: str | int
    child_theme: str | int
    topic: str | int
    metric_group: str | int
    metric: str | int
    geography_type: str | int
    geography: str | int
    geography_code: str
    age: str | int
    sex: str
    stratum: str | int
    refresh_date: str
    embargo: str | None = None
    metric_value: float | int


class IncomingHeadlineDTO(IncomingBaseDTO):
    """Data transfer object designed to consume Headline type entries from source data"""

    period_start: str
    period_end: str


class IncomingTimeSeriesDTO(IncomingBaseDTO):
    """Data transfer object designed to consume TimeSeries type entries from source data"""

    metric_frequency: str
    year: int
    epiweek: int
    month: int
    date: str
