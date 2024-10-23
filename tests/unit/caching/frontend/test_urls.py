from unittest import mock

import pytest

from caching.frontend.urls import FrontEndURLBuilder

FAKE_BASE_URL = "https://fake-base-url.com"


class TestFrontEndURLBuilder:
    @pytest.mark.parametrize(
        "input_geography_type, input_geography_name, expected_geography_type, expected_geography_name",
        (
            ["Nation", "England", "Nation", "England"],
            [
                "Lower Tier Local Authority",
                "London",
                "Lower+Tier+Local+Authority",
                "London",
            ],
            [
                "Lower Tier Local Authority",
                "Cheshire West and Chester",
                "Lower+Tier+Local+Authority",
                "Cheshire+West+and+Chester",
            ],
            [
                "Lower Tier Local Authority",
                "Bristol, City of",
                "Lower+Tier+Local+Authority",
                "Bristol%2C+City+of",
            ],
            [
                "Lower Tier Local Authority",
                "St. Helens",
                "Lower+Tier+Local+Authority",
                "St.+Helens",
            ],
            [
                "Lower Tier Local Authority",
                "Stoke-on-Trent",
                "Lower+Tier+Local+Authority",
                "Stoke-on-Trent",
            ],
        ),
    )
    def test_build_query_params_for_area_selector_page(
        self,
        input_geography_type: str,
        input_geography_name: str,
        expected_geography_type: str,
        expected_geography_name: str,
    ):
        """
        Given the names of a geography and geography type
        When `build_query_params_for_area_selector_page()` is called
            from an instance of the `FrontEndURLBuilder`
        Then a dict is returned which represents the query parameters
        """
        # Given
        frontend_url_builder = FrontEndURLBuilder(base_url=mock.Mock())

        # When
        params: dict[str, str] = (
            frontend_url_builder.build_query_params_for_area_selector_page(
                geography_type_name=input_geography_type,
                geography_name=input_geography_name,
            )
        )

        # Then
        expected_params = {
            "areaType": expected_geography_type,
            "areaName": expected_geography_name,
        }
        assert params == expected_params
