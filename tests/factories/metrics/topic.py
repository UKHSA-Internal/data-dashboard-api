import factory

from metrics.data.models.core_models import Topic


class TopicFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Topic` instances for tests
    """

    class Meta:
        model = Topic
