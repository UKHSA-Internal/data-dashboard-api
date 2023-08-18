import factory

from tests.fakes.models.metrics.geography import FakeGeography
from tests.fakes.models.metrics.geography_type import FakeGeographyType


class FakeGeographyFactory(factory.Factory):
    """
    Factory for creating `FakeGeography` instances for tests
    """

    class Meta:
        model = FakeGeography

    @classmethod
    def build_example(
        cls,
        geography_name: str = "England",
        geography_type_name: str = "Nation",
    ) -> FakeGeography:
        geography_type = FakeGeographyType(name=geography_type_name)
        return cls.build(name=geography_name, geography_type=geography_type)
