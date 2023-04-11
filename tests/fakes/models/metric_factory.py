import factory

from .metric import FakeMetric
from .topic import FakeTopic


class FakeMetricFactory(factory.Factory):
    """
    Factory for creating `FakeMetric` instances for tests
    """

    class Meta:
        model = FakeMetric

    @classmethod
    def build_example_metric(
        cls, metric_name: str = "new_cases_daily", topic_name: str = "COVID-19"
    ) -> FakeMetric:
        topic = FakeTopic(name=topic_name)
        return cls.build(name=metric_name, topic=topic)
