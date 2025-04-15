import factory

from tests.fakes.models.metrics.metric import FakeMetric
from tests.fakes.models.metrics.sub_theme import FakeSubTheme
from tests.fakes.models.metrics.theme import FakeTheme


class FakeSubThemeFactory(factory.Factory):
    """
    Factory for creating `FakeSubTheme` instances for tests
    """

    class Meta:
        model = FakeSubTheme

    @classmethod
    def build_example_sub_theme(
        cls,
        name: str,
        theme: FakeTheme,
    ) -> FakeSubTheme:
        return cls.build(name=name, theme=theme)
