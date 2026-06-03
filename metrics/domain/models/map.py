import datetime

from pydantic.main import BaseModel

from metrics.domain.models.common import BaseRequestParams

OPTIONAL_STRING = str | None


class MapMainParameters(BaseModel):
    theme: str
    sub_theme: str
    topic: str
    metric: str
    stratum: str
    age: str
    sex: str
    geography_type: str
    geographies: list[str]


class MapAccompanyingPointOptionalParameters(BaseModel):
    theme: OPTIONAL_STRING
    sub_theme: OPTIONAL_STRING
    topic: OPTIONAL_STRING
    metric: OPTIONAL_STRING
    stratum: OPTIONAL_STRING
    age: OPTIONAL_STRING
    sex: OPTIONAL_STRING
    geography_type: OPTIONAL_STRING
    geography: OPTIONAL_STRING


class MapAccompanyingPoint(BaseModel):
    label_prefix: str
    label_suffix: OPTIONAL_STRING
    parameters: MapAccompanyingPointOptionalParameters


class MapsParameters(BaseRequestParams):
    date_from: datetime.date
    date_to: datetime.date
    parameters: MapMainParameters
    accompanying_points: list[MapAccompanyingPoint]
