import factory

from tests.fakes.models.stratum import FakeStratum


class FakeStratumFactory(factory.Factory):
    """
    Factory for creating `FakeStratum` instances for tests
    """

    class Meta:
        model = FakeStratum

    @classmethod
    def build_example(cls, stratum_name: str = "default") -> FakeStratum:
        return FakeStratum(name=stratum_name)
