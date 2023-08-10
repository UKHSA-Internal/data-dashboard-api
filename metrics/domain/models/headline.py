from typing import Optional

from pydantic.main import BaseModel


class HeadlineParameters(BaseModel):
    topic: str
    metric: str
    stratum: str | None = ""
    geography: str | None = ""
    geography_type: str | None = ""
    sex: str | None = ""
    age: str | None = ""

    @property
    def topic_name(self) -> str:
        return self.topic

    @property
    def metric_name(self) -> str:
        return self.metric

    @property
    def geography_name(self) -> Optional[str]:
        return self.geography or ""

    @property
    def geography_type_name(self) -> Optional[str]:
        return self.geography_type or ""

    @property
    def stratum_name(self) -> Optional[str]:
        return self.stratum or ""

    @property
    def age_name(self) -> Optional[str]:
        return self.age or ""

    @property
    def sex_name(self):
        return self.sex or ""
