from typing import Dict, List, Union

from pydantic import BaseModel


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


class Ingestion:
    def __init__(self, data):
        self.data = data

    def convert_to_models(self) -> List[HeadlineDTO]:
        return [self.to_model(record) for record in self.data]

    @staticmethod
    def to_model(data: Dict[str, Union[str, float]]) -> HeadlineDTO:
        return HeadlineDTO(
            theme=data["parent_theme"],
            sub_theme=data["child_theme"],
            metric_group=data["metric_group"],
            topic=data["topic"],
            metric=data["metric"],
            geography_type=data["geography_type"],
            geography=data["geography"],
            age=data["age"],
            sex=data["sex"],
            stratum=data["stratum"],
            period_start=data["period_start"],
            period_end=data["period_end"],
            metric_value=data["metric_value"],
            refresh_date=data["refresh_date"],
        )
