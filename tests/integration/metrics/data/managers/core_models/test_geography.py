import pytest

from metrics.data.models.core_models.supporting import Geography, GeographyType
from tests.factories.metrics.geography import GeographyFactory
from tests.factories.metrics.geography_type import GeographyTypeFactory


class TestGeographyManager:
    @pytest.mark.django_db
    def test_query_for_get_all_names_and_ids(self):
        """
        Given a number of existing `GeographyType` records
        When `get_all_names_and_ids` is called
        Then the geography types with their IDs and names are returned correctly
        """
        # Given
        fake_geography_type_name_one = "Nation"
        fake_geography_type_name_two = "Region"
        fake_geography_name_one = "England"
        fake_geography_name_two = "North west"

        geography_type_one = GeographyTypeFactory(
            name=fake_geography_type_name_one,
            with_geographies=[fake_geography_name_one],
        )
        geography_type_two = GeographyTypeFactory(
            name=fake_geography_type_name_two,
            with_geographies=[fake_geography_name_two],
        )

        # When
        all_geography_type_names_and_ids = GeographyType.objects.get_all_names_and_ids()

        # Then
        assert all_geography_type_names_and_ids.count() == 2

        # Access the dictionary returned by .first()
        first_result = all_geography_type_names_and_ids.first()
        assert first_result["id"] == geography_type_one.id
        assert first_result["name"] == fake_geography_type_name_one

        # Verify both records are present with correct structure
        result_list = list(all_geography_type_names_and_ids)
        assert result_list[0] == {
            "id": geography_type_one.id,
            "name": fake_geography_type_name_one,
        }
        assert result_list[1] == {
            "id": geography_type_two.id,
            "name": fake_geography_type_name_two,
        }

    @pytest.mark.django_db
    def test_query_for_get_all_names_and_codes(self):
        """
        Given a number of existing `geography` records
        When `get_all_names_and_codes` is called
        Then the geography types with their IDs and names are returned correctly
        """
        geography_one = GeographyFactory.create_with_geography_type(
            name="Leeds",
            geography_code="E08000035",
            geography_type="Lower Tier Local Authority",
        )

        geography_two = GeographyFactory.create_with_geography_type(
            name="London", geography_code="E12000007", geography_type="Region"
        )
        GeographyFactory.create_with_geography_type(
            name="England",
            geography_code="E92000001",
            geography_type="Nation",
        )

        # When
        all_geography_names_and_codes = Geography.objects.get_all_names_and_codes()

        # Then
        assert all_geography_names_and_codes.count() == 3

        # Access the dictionary returned by .first()
        first_result = all_geography_names_and_codes.first()
        assert first_result["geography_code"] == geography_one.geography_code
        assert first_result["name"] == geography_one.name

        # Verify both records are present with correct structure
        result_list = list(all_geography_names_and_codes)
        assert result_list[0] == {
            "geography_code": geography_one.geography_code,
            "name": geography_one.name,
        }
        assert result_list[1] == {
            "geography_code": geography_two.geography_code,
            "name": geography_two.name,
        }

    @pytest.mark.django_db
    def test_get_name_by_code(self):
        """
        Given a number of existing `geography` records
        When `get_name_by_id` is called
        Then the geography types with their codes and names are returned correctly
        """
        GeographyFactory.create_with_geography_type(
            name="Leeds",
            geography_code="E08000035",
            geography_type="Lower Tier Local Authority",
        )

        geography_two = GeographyFactory.create_with_geography_type(
            name="London", geography_code="E12000007", geography_type="Region"
        )

        # When
        get_name_by_code = Geography.objects.get_name_by_code(
            geography_code="E12000007")

        # Access the dictionary returned by .first()
        result = get_name_by_code
        assert result == geography_two.name
