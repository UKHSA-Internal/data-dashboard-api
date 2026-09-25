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

    @mock.patch.object(
        GeographyQuerySet, "get_geography_codes_and_names_by_geography_type_id"
    )
    def test_get_geography_codes_and_names_by_geography_type_id(
        self, spy_get_geography_codes_and_names_by_geography_type_id: mock.MagicMock
    ):
        """
        Given a payload containing the required field
        When `get_all_geography_names_by_type` is called,
        Then it delegates call to `GeographyQuerySet`.
        """
        # Given
        fake_geography_type_id = "1"
        geography_manager = GeographyManager()

        # When
        GeographyManager.get_geography_codes_and_names_by_geography_type_id(
            geography_manager,
            geography_type_id=fake_geography_type_id,
        )

        # Then
        spy_get_geography_codes_and_names_by_geography_type_id.assert_called_with(
            geography_type_id=fake_geography_type_id,
        )

    @mock.patch.object(GeographyQuerySet, "get_name_by_code")
    def test_get_name_by_code(self, spy_get_name_by_code: mock.MagicMock):
        """
        Given a payload containing the required field
        When `get_name_by_id` is called,
        Then it delegates call to `GeographyQuerySet`.
        """
        # Given
        fake_geography_code = "E92000001"
        geography_manager = GeographyManager()

        # When
        GeographyManager.get_name_by_code(
            geography_manager,
            geography_code=fake_geography_code,
        )

        # Then
        spy_get_name_by_code.assert_called_with(fake_geography_code)

    def test_get_geography_type_id_and_code_by_name_found(self):
        """
        Given a geography name and geography type name that exist
        When `get_geography_type_id_and_code_by_name` is called,
        Then it returns the geography_type_id and geography_code.
        """
        # Given
        fake_geography_name = "England"
        fake_geography_type_name = "Nation"
        fake_geography_type_id = 1
        fake_geography_code = "E92000001"

        mock_record = mock.Mock()
        mock_record.geography_type_id = fake_geography_type_id
        mock_record.geography_code = fake_geography_code

        geography_manager = GeographyManager()

        mock_queryset = mock.Mock()
        mock_queryset.filter.return_value.first.return_value = mock_record

        # When
        with mock.patch.object(
            geography_manager,
            "select_related",
            return_value=mock_queryset,
        ):
            result = geography_manager.get_geography_type_id_and_code_by_name(
                geography_manager,
                geography_name=fake_geography_name,
                geography_type_name=fake_geography_type_name,
            )

        # Then
        assert result == (fake_geography_type_id, fake_geography_code)

    def test_get_geography_type_id_and_code_by_name_not_found(self):
        """
        Given a geography name and geography type name that do not exist
        When `get_geography_type_id_and_code_by_name` is called,
        Then it returns (None, None).
        """
        # Given
        fake_geography_name = "NonexistentCountry"
        fake_geography_type_name = "NonexistentType"

        geography_manager = GeographyManager()

        mock_queryset = mock.Mock()
        mock_queryset.filter.return_value.first.return_value = None

        # When
        with mock.patch.object(
            geography_manager,
            "select_related",
            return_value=mock_queryset,
        ):
            result = geography_manager.get_geography_type_id_and_code_by_name(
                geography_manager,
                geography_name=fake_geography_name,
                geography_type_name=fake_geography_type_name,
            )

        # Then
        assert result == (None, None)
