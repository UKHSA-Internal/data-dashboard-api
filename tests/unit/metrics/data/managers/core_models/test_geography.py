from unittest import mock

from metrics.data.managers.core_models.geography import (
    GeographyManager,
    GeographyQuerySet,
)


class TestGeographyManager:
    @mock.patch.object(GeographyQuerySet, "get_all_geography_names_by_geography_type")
    def test_get_all_geography_names_by_type(
        self, spy_get_all_geography_names_by_type: mock.MagicMock
    ):
        """
        Given a payload containing the required field
        When `get_all_geography_names_by_type` is called,
        Then it delegates call to `GeographyQuerySet`.
        """
        # Given
        fake_geography_type = "fake_geography_type"
        geography_manager = GeographyManager()

        # When
        GeographyManager.get_all_geography_names_by_geography_type(
            geography_manager,
            geography_type_name=fake_geography_type,
        )

        # Then
        spy_get_all_geography_names_by_type.assert_called_with(
            geography_type_name=fake_geography_type,
        )
