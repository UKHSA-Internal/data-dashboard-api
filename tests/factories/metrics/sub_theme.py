import factory

from metrics.data.models.core_models import SubTheme, Theme


class SubThemeFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `SubTheme` instances for tests
    """

    class Meta:
        model = SubTheme

    @classmethod
    def create_with_theme(cls, name: str, theme: str):
        theme, _ = Theme.objects.get_or_create(name=theme)

        return cls.create(
            name=name,
            theme=theme,
        )
