import factory

from tests.fakes.models.metrics.geography import FakeGeography
from tests.fakes.models.metrics.geography_type import FakeGeographyType


class FakeGeographyTypeFactory(factory.Factory):
    """
    Factory for creating `FakeGeographyType` instances for tests
    """

    class Meta:
        model = FakeGeographyType

    @classmethod
    def build_example(
        cls,
        geography_type_name: str = "Nation",
    ) -> FakeGeography:
        return cls.build(id=1, name=geography_type_name)
