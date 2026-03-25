import factory

from metrics.data.models.core_models import Topic, SubTheme


class TopicFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Topic` instances for tests
    """

    class Meta:
        model = Topic

    @classmethod
    def create_with_sub_theme(
        cls, name: str, sub_theme: str
    ):
        sub_theme, _ = SubTheme.objects.get_or_create(name=sub_theme)

        return cls.create(
            name=name,
            sub_theme=sub_theme,
        )
