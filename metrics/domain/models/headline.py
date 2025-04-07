from pydantic.main import BaseModel
from rest_framework.request import Request


class HeadlineParameters(BaseModel):
    topic: str
    metric: str
    stratum: str | None = ""
    geography: str | None = ""
    geography_type: str | None = ""
    sex: str | None = ""
    age: str | None = ""
    request: Request | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def topic_name(self) -> str:
        return self.topic

    @property
    def metric_name(self) -> str:
        return self.metric

    @property
    def geography_name(self) -> str:
        return self.geography or ""

    @property
    def geography_type_name(self) -> str:
        return self.geography_type or ""

    @property
    def stratum_name(self) -> str:
        return self.stratum or ""

    @property
    def age_name(self) -> str:
        return self.age or ""

    @property
    def sex_name(self) -> str:
        return self.sex or ""
