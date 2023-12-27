import factory

from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.metric_group import FakeMetricGroup
from tests.fakes.models.metrics.sub_theme import FakeSubTheme
from tests.fakes.models.metrics.theme import FakeTheme
from tests.fakes.models.metrics.topic import FakeTopic


class FakeMetricFactory(factory.Factory):
    """
    Factory for creating `FakeMetric` instances for tests
    """

    class Meta:
        model = FakeMetric

    @classmethod
    def build_example_metric(
        cls,
        metric_name: str = "COVID-19_deaths_ONSByDay",
        metric_group_name: str = "deaths",
        topic_name: str = "COVID-19",
        theme_name: str = "infectious_disease",
        sub_theme_name: str = "respiratory",
    ) -> FakeMetric:
        theme = FakeTheme(name=theme_name)
        sub_theme = FakeSubTheme(name=sub_theme_name, theme=theme)
        topic = FakeTopic(name=topic_name, sub_theme=sub_theme)
        metric_group = FakeMetricGroup(name=metric_group_name, topic=topic)
        return cls.build(name=metric_name, metric_group=metric_group, topic=topic)
