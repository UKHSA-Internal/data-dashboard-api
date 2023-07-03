from pydantic.main import BaseModel


class HeadlineDTO(BaseModel):
    theme: str
    sub_theme: str
    topic: str
    metric_group: str
    metric: str
    geography_type: str
    geography: str
    age: str
    sex: str
    stratum: str

    period_start: str
    period_end: str
    refresh_date: str

    metric_value: float
