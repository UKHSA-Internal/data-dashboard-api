from enum import Enum

import pytest
from unittest.mock import MagicMock, patch

from validation.geography_code import UNITED_KINGDOM_GEOGRAPHY_CODE
from metrics.data.in_memory_models.geography_relationships.handlers import (
    get_upstream_relationships_for_geography,
    get_downstream_relationships_for_geography,
    _get_ltla_from_utlas,
)
from metrics.data.in_memory_models.geography_relationships.region_to_nation import (
    ENGLAND_GEOGRAPHY_CODE,
)


# helper function
def _dict_like_mock():
    m = MagicMock()
    m._data = {}
    m.__getitem__.side_effect = lambda key: m._data[key]
    m.__setitem__.side_effect = lambda key, value: m._data.__setitem__(key, value)
    return m


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


class TestGetLtlaFromUtlas:

    def test_single_utla(self):
        with patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UTLAtoLTLA",
            new=_dict_like_mock(),
        ) as mockUTLAtoLTLA:

            mockUTLAtoLTLA["UTLA1"] = MagicMock()
            mockUTLAtoLTLA["UTLA1"].return_list.return_value = ["LTLA1", "LTLA2"]

            result = _get_ltla_from_utlas(["utla1"])
            assert result == ["LTLA1", "LTLA2"]

    def test_multiple_utlas(self):
        with patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UTLAtoLTLA",
            new=_dict_like_mock(),
        ) as mockUTLAtoLTLA:

            mockUTLAtoLTLA["UTLA1"] = MagicMock()
            mockUTLAtoLTLA["UTLA1"].return_list.return_value = ["LTLA1"]

            mockUTLAtoLTLA["UTLA2"] = MagicMock()
            mockUTLAtoLTLA["UTLA2"].return_list.return_value = ["LTLA2A", "LTLA2B"]

            result = _get_ltla_from_utlas(["utla1", "utla2"])
            assert result == ["LTLA1", "LTLA2A", "LTLA2B"]

    def test_empty(self):
        with patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UTLAtoLTLA",
            new=_dict_like_mock(),
        ):
            assert _get_ltla_from_utlas([]) == []


class TestDownstreamRelationships:

    @staticmethod
    def _assert_structure(result):
        assert set(result.keys()) == {
            "ukhsa_regions",
            "government_office_regions",
            "nhs_regions",
            "nhs_trusts",
            "upper_tier_local_authorities",
            "lower_tier_local_authorities",
        }

    def test_invalid_geography_type(self):
        GeographyType = MagicMock()
        GeographyType.__iter__.return_value = iter(
            [
                MagicMock(value="UKHSA Region"),
                MagicMock(value="Government Office Region"),
            ]
        )

        with patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.GeographyType",
            new=GeographyType,
        ):
            result = get_downstream_relationships_for_geography(
                "InvalidGeographyType", "London"
            )
            assert result is None

    def test_returns_none_when_key_error(self):
        GeographyType = MagicMock()
        GeographyType.__iter__.return_value = iter([MagicMock(value="UKHSA Region")])

        UKHSARegion = MagicMock()
        UKHSARegion.__getitem__.side_effect = KeyError("INVALID_KEY")

        with patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.GeographyType",
            new=GeographyType,
        ), patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UKHSARegion",
            new=UKHSARegion,
        ):

            result = get_downstream_relationships_for_geography(
                "UKHSA Region", "London"
            )
            assert result is None

    def test_ukhsa_region(self):
        #Given
        GeographyType = MagicMock()
        GeographyType.__iter__.return_value = iter([MagicMock(value="UKHSA Region")])

        UKHSARegion = MagicMock()
        UKHSARegion._members = {"LONDON": MagicMock(value="UKHSA_London")}
        UKHSARegion.__getitem__.side_effect = lambda key: UKHSARegion._members[key]

        UKHSARegionUTLAs = MagicMock()
        region_utla_mock = MagicMock()
        region_utla_mock.return_list.return_value = ["UTLA1", "UTLA2"]
        region_utla_mock.return_name_list.return_value = ["UTLA1", "UTLA2"]
        UKHSARegionUTLAs._members = {"LONDON": region_utla_mock}
        UKHSARegionUTLAs.__getitem__.side_effect = (
            lambda key: UKHSARegionUTLAs._members[key]
        )

        UTLAtoLTLA = _dict_like_mock()
        UTLAtoLTLA["UTLA1"] = MagicMock(return_list=MagicMock(return_value=["LTLA1"]))
        UTLAtoLTLA["UTLA2"] = MagicMock(return_list=MagicMock(return_value=["LTLA2"]))

        # When
        with patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.GeographyType",
            new=GeographyType,
        ), patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UKHSARegion",
            new=UKHSARegion,
        ), patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UKHSARegionUTLAs",
            new=UKHSARegionUTLAs,
        ), patch(
            "metrics.data.in_memory_models.geography_relationships.handlers.UTLAtoLTLA",
            new=UTLAtoLTLA,
        ):

            result = get_downstream_relationships_for_geography(
                "UKHSA Region", "London"
            )

        # Then
        self._assert_structure(result)
        assert result["ukhsa_regions"] == ["UKHSA_London"]
        assert result["upper_tier_local_authorities"] == ["UTLA1", "UTLA2"]
        assert result["lower_tier_local_authorities"] == ["LTLA1", "LTLA2"]


    def test_gov_office_region(self):
        GeographyType = MagicMock()
        GeographyType.__iter__.return_value = iter([
            MagicMock(value="Government Office Region")
        ])

        GovOfficeRegion = MagicMock()
        GovOfficeRegion._members = {"NORTH_WEST": MagicMock(value="GOR_NW")}
        GovOfficeRegion.__getitem__.side_effect = lambda key: GovOfficeRegion._members[key]

        GovOfficeRegionUTLAs = MagicMock()
        gor_mock = MagicMock()
        gor_mock.return_list.return_value = ["UTLA10"]
        gor_mock.return_name_list.return_value = ["UTLA10"]
        GovOfficeRegionUTLAs._members = {"NORTH_WEST": gor_mock}
        GovOfficeRegionUTLAs.__getitem__.side_effect = lambda key: GovOfficeRegionUTLAs._members[key]

        UTLAtoLTLA = _dict_like_mock()
        UTLAtoLTLA["UTLA10"] = MagicMock(return_list=MagicMock(return_value=["LTLA10"]))

        with patch("metrics.data.in_memory_models.geography_relationships.handlers.GeographyType", new=GeographyType), \
             patch("metrics.data.in_memory_models.geography_relationships.handlers.GovOfficeRegion", new=GovOfficeRegion), \
             patch("metrics.data.in_memory_models.geography_relationships.handlers.GovOfficeRegionUTLAs", new=GovOfficeRegionUTLAs), \
             patch("metrics.data.in_memory_models.geography_relationships.handlers.UTLAtoLTLA", new=UTLAtoLTLA):

            result = get_downstream_relationships_for_geography(
                "Government Office Region", "North West"
            )

        self._assert_structure(result)
        assert result["government_office_regions"] == ["GOR_NW"]
        assert result["upper_tier_local_authorities"] == ["UTLA10"]
        assert result["lower_tier_local_authorities"] == ["LTLA10"]


    def test_upper_tier_local_authority(self):
        GeographyType = MagicMock()
        GeographyType.__iter__.return_value = iter([
            MagicMock(value="Upper Tier Local Authority")
        ])

        UTLAs = MagicMock()
        UTLAs._members = {"UTLA1": MagicMock(value=["UTLA1_CODE"])}
        UTLAs.__getitem__.side_effect = lambda key: UTLAs._members[key]

        UTLAtoLTLA = _dict_like_mock()
        UTLAtoLTLA["UTLA1"] = MagicMock(return_list=MagicMock(return_value=["LTLA_X"]))

        with patch("metrics.data.in_memory_models.geography_relationships.handlers.GeographyType", new=GeographyType), \
             patch("metrics.data.in_memory_models.geography_relationships.handlers.UTLAs", new=UTLAs), \
             patch("metrics.data.in_memory_models.geography_relationships.handlers.UTLAtoLTLA", new=UTLAtoLTLA):

            result = get_downstream_relationships_for_geography(
                "Upper Tier Local Authority", "UTLA1"
            )

        self._assert_structure(result)
        assert result["upper_tier_local_authorities"] == ["UTLA1_CODE"]
        assert result["lower_tier_local_authorities"] == ["LTLA_X"]

    
    def test_lower_tier_local_authority(self):
        GeographyType = MagicMock()
        GeographyType.__iter__.return_value = iter([
            MagicMock(value="Lower Tier Local Authority")
        ])

        LTLAs = MagicMock()
        LTLAs._members = {"LTLA1": MagicMock(value=["LTLA1_CODE"])}
        LTLAs.__getitem__.side_effect = lambda key: LTLAs._members[key]

        with patch("metrics.data.in_memory_models.geography_relationships.handlers.GeographyType", new=GeographyType), \
             patch("metrics.data.in_memory_models.geography_relationships.handlers.LTLAs", new=LTLAs):

            result = get_downstream_relationships_for_geography(
                "Lower Tier Local Authority", "LTLA1"
            )

        self._assert_structure(result)
        assert result["lower_tier_local_authorities"] == ["LTLA1_CODE"]
