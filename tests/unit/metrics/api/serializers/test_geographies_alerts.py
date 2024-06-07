from unittest import mock

from metrics.api.serializers.geographies_alerts import GeographiesForAlertsSerializer
from tests.fakes.factories.metrics.headline_factory import (
    FakeCoreHeadlineFactory,
)
from tests.fakes.managers.geography_manager import FakeGeographyManager


class TestGeographiesForAlertsSerializer:
    def test_get_results(self):
        """
        Given a valid payload has been serialized
        When `data()` is called from an instance of
            `GeographiesForAlertsSerializer`
        Then the returned results contain the correct `geography_codes`
            and `geography_names`
        """
        # Given
        fake_geography_manager = FakeGeographyManager(
            geographies=[("E06000001", "North East"), ("E06000002", "North West")]
        )

        serializer = GeographiesForAlertsSerializer(
            context={
                "geography_manager": fake_geography_manager,
            },
        )

        # When
        expected_results = [("E06000001", "North East"), ("E06000002", "North West")]
        results = serializer.data()

        # Then
        assert results == expected_results

    def test_validate_geography_code_makes_correct_call(self):
        """
        Given a valid payload sent to the serializer
        When the `is_valid()` method is called
        Then True is returned
        """
        # Given
        fake_geography_manager = FakeGeographyManager(
            geographies=[("E06000001", "North East"), ("E06000002", "North West")]
        )

        request_serializer = GeographiesForAlertsSerializer(
            context={
                "geography_manager": fake_geography_manager,
            },
            data={"geography_code": "E06000001"},
        )

        # When / Then
        assert request_serializer.is_valid() is True

    def test_validate_geography_code_raise_error(self):
        """
        Given a valid payload sent to the serializer
        When the `is_valid()` method is called
        Then False is returned
        """
        # Given
        fake_geography_manager = FakeGeographyManager(
            geographies=[("E06000001", "North East"), ("E06000002", "North West")]
        )

        request_serializer = GeographiesForAlertsSerializer(
            context={
                "geography_manager": fake_geography_manager,
            },
            data={"geography_code": "invalid-code"},
        )

        # When / Then
        assert request_serializer.is_valid() is False
