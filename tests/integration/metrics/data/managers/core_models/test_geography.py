import pytest

from metrics.data.models.core_models.supporting import Geography
from tests.factories.metrics.geography_type import GeographyTypeFactory


class TestGeographyManager:
    @pytest.mark.django_db
    def test_query_for_all_geography_names_by_geography_type(
        self,
    ):
        """
        Given a number of existing `Geography` records
        When `get_all_geography_names_by_geography_type` is called
        Then the geographies have bee filtered correctly
        """
        # Given
        fake_geography_type_name_one = "Nation"
        fake_geography_type_name_two = "Region"
        fake_geography_name_one = "England"
        fake_geography_name_two = "North west"

        GeographyTypeFactory(
            name=fake_geography_type_name_one,
            with_geographies=[fake_geography_name_one],
        )
        GeographyTypeFactory(
            name=fake_geography_type_name_two,
            with_geographies=[fake_geography_name_two],
        )

        # When
        all_geography_names = Geography.objects.all()
        all_geography_names_by_type = (
            Geography.objects.get_all_geography_names_by_geography_type(
                geography_type_name=fake_geography_type_name_one
            )
        )

        # Then
        assert all_geography_names.count() == 2
        assert all_geography_names_by_type.count() == 1
        assert all_geography_names_by_type.first() == fake_geography_name_one
