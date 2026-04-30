import factory

from cms.snippets.models.menu_builder.menu import Menu, SimpleMenu


class MenuFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `Menu` instances for tests
    """

    class Meta:
        model = Menu


class SimpleMenuFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `SimpleMenu` instances for tests
    """

    class Meta:
        model = SimpleMenu
