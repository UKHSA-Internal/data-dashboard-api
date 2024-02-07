import factory

from metrics.data.models.core_models import Metric


class MetricFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Metric` instances for tests
    """

    class Meta:
        model = Metric
