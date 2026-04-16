import factory

from metrics.data.models.core_models import Theme, SubTheme


class ThemeFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Theme` instances for tests
    """

    class Meta:
        model = Theme
