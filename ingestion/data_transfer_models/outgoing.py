from pydantic import BaseModel


class OutgoingBaseDTO(BaseModel):
    """Base data transfer object providing common fields"""

    theme: str | int
    sub_theme: str | int
    topic: str | int
    metric_group: str | int
    metric: str | int
    geography_type: str | int
    geography: str | int
    age: str | int
    sex: str
    stratum: str | int
    refresh_date: str
    embargo: str | None = None
    metric_value: float


class OutgoingHeadlineDTO(OutgoingBaseDTO):
    """Data transfer object designed to provide enriched & processed data to create `CoreHeadline` records"""

    period_start: str
    period_end: str


class OutgoingTimeSeriesDTO(OutgoingBaseDTO):
    """Data transfer object designed to provide enriched & processed data to create `CoreTimeSeries` records"""

    year: int
    month: int
    epiweek: int
    date: str
    metric_frequency: str
