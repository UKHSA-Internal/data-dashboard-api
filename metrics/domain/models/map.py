import datetime
from collections.abc import Iterable

from pydantic.main import BaseModel
from rest_framework.request import Request

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


class MapsParameters(BaseModel):
    date_from: datetime.date
    date_to: datetime.date
    parameters: MapMainParameters
    accompanying_points: list[MapAccompanyingPoint]

    request: Request | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])
