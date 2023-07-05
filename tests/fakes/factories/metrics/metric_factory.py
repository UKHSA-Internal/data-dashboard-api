import factory

from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.metric_group import FakeMetricGroup
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
    ) -> FakeMetric:
        topic = FakeTopic(name=topic_name)
        metric_group = FakeMetricGroup(name=metric_group_name, topic=topic)
        return cls.build(name=metric_name, metric_group=metric_group, topic=topic)
