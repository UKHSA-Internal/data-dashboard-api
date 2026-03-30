import factory

from metrics.data.models.core_models import Metric, Topic
from metrics.data.models.core_models import Metric, Topic


class MetricFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Metric` instances for tests
    """

    class Meta:
        model = Metric

    @classmethod
    def create_with_topic(cls, name: str, topic: str):
        topic, _ = Topic.objects.get_or_create(name=topic)

        return cls.create(
            name=name,
            topic=topic,
        )
