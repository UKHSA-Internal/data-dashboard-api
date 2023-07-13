from pydantic import BaseModel


class BaseDTO(BaseModel):
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
    metric_value: float


class HeadlineDTO(BaseDTO):
    period_start: str
    period_end: str


class TimeSeriesDTO(BaseDTO):
    year: int
    month: int
    epiweek: int
    date: str
