import factory

from tests.fakes.models.metrics.theme import FakeTheme


class FakeThemeFactory(factory.Factory):
    """
    Factory for creating `FakeTheme` instances for tests
    """

    class Meta:
        model = FakeTheme

    @classmethod
    def build_example_theme(
        cls,
        name: str,
    ) -> FakeTheme:
        return cls.build(name=name)
