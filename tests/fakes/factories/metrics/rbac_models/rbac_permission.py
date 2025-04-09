import factory

from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.stratum_factory import FakeStratumFactory
from tests.fakes.models.metrics.age import FakeAge
from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.rbac_models.rbac_permission import FakeRBACPermission
from tests.fakes.models.metrics.stratum import FakeStratum


class FakeRBACPermissionFactory(factory.Factory):
    """
    Factory for creating `FakeRBACPermission` instances for tests
    """

    class Meta:
        model = FakeRBACPermission

    @classmethod
    def build_rbac_permission(
        cls,
        theme: str = "infectious_disease",
        sub_theme: str = "respiratory",
        metric: str = "COVID-19_cases_casesByDay",
        topic: str = "COVID-19",
        geography: str = "England",
        geography_type: str = "Nation",
        age: str = "all",
        stratum: str = "default",
    ) -> FakeRBACPermission:
        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric,
            topic_name=topic,
            theme_name=theme,
            sub_theme_name=sub_theme,
        )

        topic = metric.topic
        sub_theme = topic.sub_theme
        theme = sub_theme.theme

        geography = FakeGeographyFactory.build_example(
            geography_name=geography, geography_type_name=geography_type
        )
        geography_type = geography.geography_type

        stratum: FakeStratum = FakeStratumFactory.build_example(
            stratum_name=stratum,
        )
        age = FakeAge(name=age)

        return cls.build(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            metric=metric,
            geography_type=geography_type,
            geography=geography,
            stratum=stratum,
            age=age,
        )
