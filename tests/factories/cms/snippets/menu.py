import factory

from cms.snippets.models.menu_builder.menu import Menu


class MenuFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Menu` instances for tests
    """

    class Meta:
        model = Menu
