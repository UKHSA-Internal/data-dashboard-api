from unittest import mock

import pytest

from metrics.data.managers.core_models.geography import (
    GeographyManager,
    GeographyQuerySet,
)
from metrics.data.models.core_models import Geography
from tests.factories.metrics.geography import GeographyFactory


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


@pytest.mark.django_db
class TestGeographyManagerDatabaseQueries:
    @pytest.fixture
    def geography_records(self):
        nation = GeographyFactory.create_with_geography_type(
            name="England",
            geography_code="E92000001",
            geography_type="Nation",
        )
        region = GeographyFactory.create_with_geography_type(
            name="London",
            geography_code="E12000007",
            geography_type="Region",
        )
        utla = GeographyFactory.create_with_geography_type(
            name="London",
            geography_code="E09000001",
            geography_type="Upper tier local authority",
        )

        return {
            "nation": nation,
            "region": region,
            "utla": utla,
        }

    def test_get_all_names_returns_distinct_ordered_names(self, geography_records):
        assert list(Geography.objects.get_all_names()) == ["England", "London"]

    def test_get_name_by_code_returns_matching_name(self, geography_records):
        assert Geography.objects.get_name_by_code("E92000001") == "England"

    def test_get_name_by_code_returns_none_when_missing(self, geography_records):
        assert Geography.objects.get_name_by_code("missing") is None

    def test_get_id_by_name_uses_geography_type_to_disambiguate_shared_names(
        self, geography_records
    ):
        assert (
            Geography.objects.get_id_by_name(
                geography_name="London",
                geography_type_name="Region",
            )
            == geography_records["region"].id
        )

    def test_get_id_by_name_returns_none_when_pair_does_not_exist(
        self, geography_records
    ):
        assert (
            Geography.objects.get_id_by_name(
                geography_name="England",
                geography_type_name="Region",
            )
            is None
        )

    def test_get_code_by_name_uses_geography_type_to_disambiguate_shared_names(
        self, geography_records
    ):
        assert (
            Geography.objects.get_code_by_name(
                geography_name="London",
                geography_type_name="Upper tier local authority",
            )
            == "E09000001"
        )

    def test_get_code_by_name_returns_none_when_pair_does_not_exist(
        self, geography_records
    ):
        assert (
            Geography.objects.get_code_by_name(
                geography_name="England",
                geography_type_name="Region",
            )
            is None
        )

    def test_get_geography_type_id_and_code_by_name_returns_matching_pair(
        self, geography_records
    ):
        geography_type_id, geography_code = (
            Geography.objects.get_geography_type_id_and_code_by_name(
                geography_name="London",
                geography_type_name="Region",
            )
        )

        assert geography_type_id == geography_records["region"].geography_type_id
        assert geography_code == "E12000007"

    def test_get_geography_type_id_and_code_by_name_returns_none_pair_when_missing(
        self, geography_records
    ):
        assert Geography.objects.get_geography_type_id_and_code_by_name(
            geography_name="England",
            geography_type_name="Region",
        ) == (None, None)

    def test_get_all_geography_codes_by_geography_type_returns_ordered_codes(
        self, geography_records
    ):
        assert list(
            Geography.objects.get_all_geography_codes_by_geography_type(
                geography_type_name="Region",
            )
        ) == ["E12000007"]

    def test_get_all_geography_names_by_geography_type_returns_ordered_names(
        self, geography_records
    ):
        assert list(
            Geography.objects.get_all_geography_names_by_geography_type(
                geography_type_name="Region",
            )
        ) == ["London"]

    def test_get_geography_codes_and_names_by_geography_type_returns_ordered_tuples(
        self, geography_records
    ):
        assert list(
            Geography.objects.get_geography_codes_and_names_by_geography_type(
                geography_type_name="Region",
            )
        ) == [("E12000007", "London")]

    def test_get_geography_codes_and_names_by_geography_type_id_returns_ordered_dicts(
        self, geography_records
    ):
        assert list(
            Geography.objects.get_geography_codes_and_names_by_geography_type_id(
                geography_type_id=geography_records["region"].geography_type_id,
            )
        ) == [{"geography_code": "E12000007", "name": "London"}]

    def test_get_geographies_by_geography_type_returns_ordered_dicts(
        self, geography_records
    ):
        assert list(
            Geography.objects.get_geographies_by_geography_type(
                geography_type_name="Nation",
            )
        ) == [{"name": "England", "geography_code": "E92000001"}]

    def test_does_geography_code_exist_returns_true_for_matching_type(
        self, geography_records
    ):
        assert Geography.objects.does_geography_code_exist(
            geography_code="E12000007",
            geography_type_name="Region",
        )

    def test_does_geography_code_exist_returns_false_for_different_type(
        self, geography_records
    ):
        assert not Geography.objects.does_geography_code_exist(
            geography_code="E12000007",
            geography_type_name="Nation",
        )

    def test_get_geography_code_for_geography_returns_matching_code(
        self, geography_records
    ):
        assert (
            Geography.objects.get_geography_code_for_geography(
                geography="England",
                geography_type="Nation",
            )
            == "E92000001"
        )

    def test_get_all_names_and_codes_returns_records_ordered_by_code(
        self, geography_records
    ):
        assert list(Geography.objects.get_all_names_and_codes()) == [
            {"name": "London", "geography_code": "E09000001"},
            {"name": "London", "geography_code": "E12000007"},
            {"name": "England", "geography_code": "E92000001"},
        ]
