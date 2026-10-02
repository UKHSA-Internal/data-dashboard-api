import factory

from cms.common.models import CommonPage


class CommonPageFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `CommonPage` instances for tests
    """

    class Meta:
        model = CommonPage
