import factory

from tests.fakes.models.metrics.sub_theme import FakeSubTheme
from tests.fakes.models.metrics.topic import FakeTopic


class FakeTopicFactory(factory.Factory):
    """
    Factory for creating `FakeTopic` instances for tests
    """

    class Meta:
        model = FakeTopic

    @classmethod
    def build_example_topic(
        cls,
        name: str,
        sub_theme: FakeSubTheme,
    ) -> FakeTopic:
        return cls.build(name=name, sub_theme=sub_theme)
