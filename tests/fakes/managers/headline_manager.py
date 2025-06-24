import datetime

from metrics.data.managers.core_models.headline import CoreHeadlineManager
from tests.fakes.models.metrics.rbac_models.rbac_permission import FakeRBACPermission


class FakeCoreHeadlineManager(CoreHeadlineManager):
    """
    A fake version of the `CoreHeadlineManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, headlines, **kwargs):
        self.headlines = headlines
        super().__init__(**kwargs)

    def get_latest_headline(
        self,
        *,
        topic: str,
        metric: str,
        geography: str | None = None,
        geography_type: str | None = None,
        geography_code: str | None = None,
        stratum: str | None = None,
        sex: str | None = None,
        age: str | None = None,
        rbac_permissions: list[FakeRBACPermission] = None
    ) -> tuple[float, datetime.date] | None:
        filtered_headlines = [
            core_headline
            for core_headline in self.headlines
            if core_headline.metric.metric_group.topic.name == topic
            if core_headline.metric.name == metric
        ]

        if geography:
            filtered_headlines = [
                x for x in filtered_headlines if x.geography.name == geography
            ]

        if geography_code:
            filtered_headlines = [
                x
                for x in filtered_headlines
                if x.geography.geography_code == geography_code
            ]

        if geography_type:
            filtered_headlines = [
                x
                for x in filtered_headlines
                if x.geography.geography_type.name == geography_type
            ]

        if stratum:
            filtered_headlines = [
                x for x in filtered_headlines if x.stratum.name == stratum
            ]

        if sex:
            filtered_headlines = [x for x in filtered_headlines if x.sex == sex]

        if age:
            filtered_headlines = [x for x in filtered_headlines if x.age.name == age]

        try:
            return filtered_headlines[0]
        except IndexError:
            return None
