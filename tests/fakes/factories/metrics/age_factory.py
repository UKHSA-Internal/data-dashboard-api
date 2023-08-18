import factory

from tests.fakes.models.metrics.age import FakeAge


class FakeAgeFactory(factory.Factory):
    """
    Factory for creating `FakeAge` instances for tests
    """

    class Meta:
        model = FakeAge

    @classmethod
    def build_example(cls, age_name: str = "all") -> FakeAge:
        return cls.build(name=age_name)
