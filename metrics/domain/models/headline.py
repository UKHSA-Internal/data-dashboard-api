from metrics.domain.models.common import BaseRequestParams


class HeadlineParameters(BaseRequestParams):
    theme: str
    sub_theme: str
    topic: str
    metric: str
    stratum: str
    geography: str
    geography_type: str
    sex: str
    age: str
    is_public: bool | None = True
    data_classification: str | None = None

    @property
    def theme_name(self) -> str:
        return self.theme

    @property
    def sub_theme_name(self) -> str:
        return self.sub_theme

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
            "theme": self.theme_name,
            "sub_theme": self.sub_theme_name,
            "topic": self.topic_name,
            "metric": self.metric_name,
            "geography": self.geography_name,
            "geography_type": self.geography_type_name,
            "stratum": self.stratum_name,
            "age": self.age_name,
            "sex": self.sex_name,
            "rbac_permissions": self.rbac_permissions,
        }
