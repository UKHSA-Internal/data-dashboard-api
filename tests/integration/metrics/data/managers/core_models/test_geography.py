import pytest

from metrics.data.models.core_models.supporting import GeographyType
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
