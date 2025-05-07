import factory

from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.geography_type_factory import (
    FakeGeographyTypeFactory,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.sub_theme_factory import FakeSubThemeFactory
from tests.fakes.factories.metrics.theme_factory import FakeThemeFactory
from tests.fakes.factories.metrics.topic_factory import FakeTopicFactory
from tests.fakes.models.metrics.rbac_models.rbac_permission import FakeRBACPermission


class FakeRBACPermissionFactory(factory.Factory):
    """
    Factory for creating `FakeRBACPermission` instances for tests
    """

    class Meta:
        model = FakeRBACPermission

    @classmethod
    def build_rbac_permission(
        cls,
        theme: str = "",
        sub_theme: str = "",
        metric: str = "",
        topic: str = "",
        geography: str = "",
        geography_type: str = "",
    ) -> FakeRBACPermission:
        if theme:
            fake_theme = FakeThemeFactory.build_example_theme(name=theme)
        else:
            fake_theme = None

        if sub_theme:
            fake_sub_theme = FakeSubThemeFactory.build_example_sub_theme(
                name=sub_theme, theme=fake_theme
            )
        else:
            fake_sub_theme = None

        if topic:
            fake_topic = FakeTopicFactory.build_example_topic(
                name=topic, sub_theme=fake_sub_theme
            )
        else:
            fake_topic = None

        if metric:
            fake_metric = FakeMetricFactory.build(
                name=metric,
                topic=fake_topic,
            )
        else:
            fake_metric = None

        if geography_type:
            fake_geography_type = FakeGeographyTypeFactory.build_example(
                geography_type_name=geography_type
            )
        else:
            fake_geography_type = None

        if geography:
            fake_geography = FakeGeographyFactory.build(
                name=geography, geography_type=fake_geography_type
            )
        else:
            fake_geography = None

        return cls.build(
            theme=fake_theme,
            sub_theme=fake_sub_theme,
            topic=fake_topic,
            metric=fake_metric,
            geography_type=fake_geography_type,
            geography=fake_geography,
        )
