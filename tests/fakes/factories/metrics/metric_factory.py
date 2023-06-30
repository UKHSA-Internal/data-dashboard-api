import factory

from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.topic import FakeTopic


class FakeMetricFactory(factory.Factory):
    """
    Factory for creating `FakeMetric` instances for tests
    """

    class Meta:
        model = FakeMetric

    @classmethod
    def build_example_metric(
        cls, metric_name: str = "COVID-19_deaths_ONSByDay", topic_name: str = "COVID-19"
    ) -> FakeMetric:
        topic = FakeTopic(name=topic_name)
        return cls.build(name=metric_name, topic=topic)
