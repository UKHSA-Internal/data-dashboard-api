import factory

from cms.topic.models import TopicPage


class TopicPageFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Topic` instances for tests
    """

    class Meta:
        model = TopicPage
