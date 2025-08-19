from ingestion.data_transfer_models.validation.geography_code import (
    UNITED_KINGDOM_GEOGRAPHY_CODE,
)
from metrics.data.in_memory_models.geography_relationships.handlers import (
    get_upstream_relationships_for_geography,
)
from metrics.data.in_memory_models.geography_relationships.region_to_nation import (
    ENGLAND_GEOGRAPHY_CODE,
)


class TestGetUpstreamRelationshipsForGeography:
    def test_nation_relationships(self):
        """
        Given the geography code and geography type for the `Nation` of `England`
        When `get_upstream_relationships_for_geography()` is called
        Then the expected upstream relationships are returned
        """
        # Given
        geography_code = ENGLAND_GEOGRAPHY_CODE
        geography_type = "Nation"

        # When
        relationships: list[dict[str, str]] = get_upstream_relationships_for_geography(
            geography_code=geography_code,
            geography_type=geography_type,
        )

        # Then
        expected_relationships = [
            {
                "geography_type": "United Kingdom",
                "name": "United Kingdom",
                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
            }
        ]
        assert relationships == expected_relationships

    def test_nation_returns_none_when_cannot_be_mapped(self):
        """
        Given an invalid geography code for the type of `Region`
        When `get_upstream_relationships_for_geography()` is called
        Then None is returned for the relationship of `Nation`
        """
        # Given
        invalid_geography_code = "E000000000"
        geography_type = "Region"

        # When
        relationships: list[dict[str, str]] = get_upstream_relationships_for_geography(
            geography_code=invalid_geography_code,
            geography_type=geography_type,
        )

        # Then
        expected_relationships = [
            {
                "geography_type": "United Kingdom",
                "name": "United Kingdom",
                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
            },
            {
                "geography_type": "Nation",
                "name": None,
                "geography_code": None,
            },
        ]
        assert relationships == expected_relationships

    def test_region_relationships(self):
        """
        Given the geography code and geography type for the `Region` of `London`
        When `get_upstream_relationships_for_geography()` is called
        Then the expected upstream relationships are returned
        """
        # Given
        geography_code = "E12000007"
        geography_type = "Region"

        # When
        relationships: list[dict[str, str]] = get_upstream_relationships_for_geography(
            geography_code=geography_code,
            geography_type=geography_type,
        )

        # Then
        expected_relationships = [
            {
                "geography_type": "United Kingdom",
                "name": "United Kingdom",
                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
            },
            {
                "geography_type": "Nation",
                "name": "England",
                "geography_code": ENGLAND_GEOGRAPHY_CODE,
            },
        ]
        assert relationships == expected_relationships

    def test_region_returns_none_when_cannot_be_mapped(self):
        """
        Given an invalid geography code for the type of `Upper Tier Local Authority`
        When `get_upstream_relationships_for_geography()` is called
        Then None is returned for the relationship of `Region`
        """
        # Given
        invalid_geography_code = "E000000000"
        geography_type = "Upper Tier Local Authority"

        # When
        relationships: list[dict[str, str]] = get_upstream_relationships_for_geography(
            geography_code=invalid_geography_code,
            geography_type=geography_type,
        )

        # Then
        expected_relationships = [
            {
                "geography_type": "United Kingdom",
                "name": "United Kingdom",
                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
            },
            {
                "geography_type": "Region",
                "name": None,
                "geography_code": None,
            },
            {
                "geography_type": "Nation",
                "name": None,
                "geography_code": None,
            },
        ]
        assert relationships == expected_relationships

    def test_utla_relationships(self):
        """
        Given the geography code and geography type
            for the `Upper Tier Local Authority` of `Manchester`
        When `get_upstream_relationships_for_geography()` is called
        Then the expected upstream relationships are returned
        """
        # Given
        geography_code = "E08000003"
        geography_type = "Upper Tier Local Authority"

        # When
        relationships: list[dict[str, str]] = get_upstream_relationships_for_geography(
            geography_code=geography_code,
            geography_type=geography_type,
        )

        # Then
        expected_relationships = [
            {
                "geography_type": "United Kingdom",
                "name": "United Kingdom",
                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
            },
            {
                "geography_type": "Region",
                "name": "North West",
                "geography_code": "E12000002",
            },
            {
                "geography_type": "Nation",
                "name": "England",
                "geography_code": ENGLAND_GEOGRAPHY_CODE,
            },
        ]
        assert relationships == expected_relationships

    def test_returns_none_when_unsupported_geography_type_is_given(self):
        """
        Given the geography code and geography type
            for an unsupported geography type
        When `get_upstream_relationships_for_geography()` is called
        Then None is returned for the expected upstream relationships
        """
        # Given
        geography_code = "E07000229"
        geography_type = "Lower Tier Local Authority"

        # When
        relationships = get_upstream_relationships_for_geography(
            geography_code=geography_code,
            geography_type=geography_type,
        )

        # Then
        assert relationships is None
