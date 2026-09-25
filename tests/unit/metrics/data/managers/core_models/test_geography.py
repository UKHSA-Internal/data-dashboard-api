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

    @mock.patch.object(GeographyQuerySet, "get_geography_type_id_and_code_by_name")
    def test_get_geography_type_id_and_code_by_name_delegates_to_queryset(
        self, spy_get_geography_type_id_and_code_by_name: mock.MagicMock
    ):
        """
        Given a geography name and geography type name that exist
        When `get_geography_type_id_and_code_by_name` is called on the manager,
        Then it delegates call to `GeographyQuerySet`.
        """
        # Given
        fake_geography_name = "England"
        fake_geography_type_name = "Nation"
        fake_geography_type_id = 1
        fake_geography_code = "E92000001"
        expected_result = (fake_geography_type_id, fake_geography_code)

        spy_get_geography_type_id_and_code_by_name.return_value = expected_result
        geography_manager = GeographyManager()

        # When
        result = geography_manager.get_geography_type_id_and_code_by_name(
            geography_name=fake_geography_name,
            geography_type_name=fake_geography_type_name,
        )

        # Then
        assert result == expected_result
        spy_get_geography_type_id_and_code_by_name.assert_called_with(
            fake_geography_name,
            fake_geography_type_name,
        )

    def test_get_geography_type_id_and_code_by_name_queryset_found(self):
        """
        Given a queryset with a matching geography record
        When `get_geography_type_id_and_code_by_name` is called on the queryset,
        Then it returns a tuple of (geography_type_id as int, geography_code).
        """
        # Given
        fake_geography_name = "England"
        fake_geography_type_name = "Nation"
        fake_geography_type_id = 1
        fake_geography_code = "E92000001"

        mock_record = mock.Mock()
        mock_record.geography_type_id = fake_geography_type_id
        mock_record.geography_code = fake_geography_code

        mock_queryset = mock.Mock(spec=GeographyQuerySet)
        mock_queryset.select_related.return_value.filter.return_value.first.return_value = (
            mock_record
        )

        # When
        result = GeographyQuerySet.get_geography_type_id_and_code_by_name(
            mock_queryset,
            geography_name=fake_geography_name,
            geography_type_name=fake_geography_type_name,
        )

        # Then
        assert result == (fake_geography_type_id, fake_geography_code)
        assert isinstance(result[0], int)
        mock_queryset.select_related.assert_called_once_with("geography_type")
        mock_queryset.select_related.return_value.filter.assert_called_once_with(
            name=fake_geography_name,
            geography_type__name=fake_geography_type_name,
        )

    def test_get_geography_type_id_and_code_by_name_queryset_not_found(self):
        """
        Given a queryset with no matching geography record
        When `get_geography_type_id_and_code_by_name` is called on the queryset,
        Then it returns (None, None).
        """
        # Given
        fake_geography_name = "NonexistentCountry"
        fake_geography_type_name = "NonexistentType"

        mock_queryset = mock.Mock(spec=GeographyQuerySet)
        mock_queryset.select_related.return_value.filter.return_value.first.return_value = (
            None
        )

        # When
        result = GeographyQuerySet.get_geography_type_id_and_code_by_name(
            mock_queryset,
            geography_name=fake_geography_name,
            geography_type_name=fake_geography_type_name,
        )

        # Then
        assert result == (None, None)
        mock_queryset.select_related.assert_called_once_with("geography_type")
        mock_queryset.select_related.return_value.filter.assert_called_once_with(
            name=fake_geography_name,
            geography_type__name=fake_geography_type_name,
        )
