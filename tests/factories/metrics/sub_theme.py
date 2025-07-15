import factory

from metrics.data.models.core_models import SubTheme


class SubThemeFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `SubTheme` instances for tests
    """

    class Meta:
        model = SubTheme
