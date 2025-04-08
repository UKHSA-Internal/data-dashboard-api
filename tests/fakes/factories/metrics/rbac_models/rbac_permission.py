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
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
        metric_name: str = "COVID-19_cases_casesByDay",
        topic_name: str = "COVID-19",
        geography_name: str = "England",
        geography_type_name: str = "Nation",
        age_name: str = "all",
        stratum_name: str = "default",
    ) -> FakeRBACPermission:
        metric: FakeMetric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name,
            topic_name=topic_name,
            theme_name=theme_name,
            sub_theme_name=sub_theme_name,
        )

        topic = metric.topic
        sub_theme = topic.sub_theme
        theme = sub_theme.theme

        geography = FakeGeographyFactory.build_example(
            geography_name=geography_name, geography_type_name=geography_type_name
        )
        geography_type = geography.geography_type

        stratum: FakeStratum = FakeStratumFactory.build_example(
            stratum_name=stratum_name,
        )
        age = FakeAge(name=age_name)

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
