from collections.abc import Iterable

from pydantic import ConfigDict
from pydantic.main import BaseModel
from rest_framework.request import Request


class HeadlineParameters(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    topic: str
    metric: str
    stratum: str
    geography: str
    geography_type: str
    sex: str
    age: str
    request: Request | None = None

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

    def to_dict_for_query(self) -> dict[str, str]:
        """Returns a dict representation of the model used for the corresponding query.

        Returns:
            Dict[str, str]: A dict representation of the model.
                Where the keys are the names of the fields
                and the values are the values of those fields.
                E.g.
                    >>> {"topic_name": "COVID-19", ...}

        """
        return {
            "topic": self.topic_name,
            "metric": self.metric_name,
            "geography": self.geography_name,
            "geography_type": self.geography_type_name,
            "stratum": self.stratum_name,
            "age": self.age_name,
            "sex": self.sex_name,
            "rbac_permissions": self.rbac_permissions,
        }

    @property
    def rbac_permissions(self) -> Iterable["RBACPermission"]:
        return getattr(self.request, "rbac_permissions", [])
