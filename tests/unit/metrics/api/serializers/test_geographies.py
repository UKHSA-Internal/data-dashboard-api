from metrics.api.serializers.geographies import (
    GeographySerializer,
    GeographyTypesSerializer,
)
from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.geography_type_factory import (
    FakeGeographyTypeFactory,
)


class TestGeographySerializer:
    def test_returns_expected_serialized_data(self):
        """
        Given a `Geography` object
        When the object is serialized with the `GeographySerializer`
        Then the correct data is returned
        """
        # Given
        fake_geography = FakeGeographyFactory.build_example()

        # When
        serializer = GeographySerializer(instance=fake_geography)

        # Then
        serialized_data = serializer.data
        assert serialized_data["name"] == fake_geography.name
        assert serialized_data["id"] == fake_geography.id


class TestGeographyTypesSerializer:
    def test_returns_expected_serialized_data(self):
        """
        Given a `GeographyType` object
        When the object is serialized with the `GeographyTypesSerializer`
        Then the correct data is returned
        """
        # Given
        fake_geography_type = FakeGeographyTypeFactory.build_example()

        # When
        serializer = GeographyTypesSerializer(instance=fake_geography_type)

        # Then
        serialized_data = serializer.data
        assert serialized_data["name"] == fake_geography_type.name
        assert serialized_data["id"] == fake_geography_type.id
