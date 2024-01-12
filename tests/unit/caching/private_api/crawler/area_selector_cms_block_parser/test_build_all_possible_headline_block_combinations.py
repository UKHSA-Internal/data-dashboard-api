import copy
from unittest import mock

from caching.private_api.crawler.area_selector_cms_block_parser import (
    AreaSelectorCMSBlockParser,
)
from caching.private_api.crawler.geographies_crawler import GeographyTypeData


class TestBuildAllPossibleHeadlineBlockCombinations:
    def test_returns_expected_combinations(self):
        """
        Given a list of enriched `GeographyTypeData` models
            returned from the `process_geographies_api()` method
            on the `GeographyAPICrawler`
        And a base headline block
        When `build_all_possible_headline_block_combinations()` is called
            from an instance of the `AreaSelectorCMSBlockParser`
        Then each geography combination is imposed on
            a copy of the base headline block to result
            in the expected headline combinations
        """
        # Given
        geography_type_data_combinations = [
            GeographyTypeData(name="Nation", geography_names=["England", "Wales"]),
            GeographyTypeData(
                name="Lower Tier Local Authority", geography_names=["Crawley"]
            ),
        ]
        mocked_geographies_api_crawler = mock.Mock()
        mocked_geographies_api_crawler.process_geographies_api.return_value = (
            geography_type_data_combinations
        )

        base_headline_block = {
            "type": "headline_number",
            "value": {
                "topic": "Influenza",
                "metric": "influenza_headline_ICUHDUadmissionRateLatest",
                "geography": "England",
                "geography_type": "Nation",
                "sex": "all",
                "age": "all",
                "stratum": "default",
                "body": "Hospital admission rate (per 100,000)",
            },
            "id": "0520e9d6-794f-4616-b217-f5ec884a86d8",
        }
        area_selector_cms_block_parser = AreaSelectorCMSBlockParser(
            geographies_api_crawler=mocked_geographies_api_crawler
        )

        # When
        all_possible_headline_blocks = area_selector_cms_block_parser.build_all_possible_headline_block_combinations(
            headline_block=base_headline_block
        )

        # Then
        assert len(all_possible_headline_blocks) == 3
        headline_block_for_england = base_headline_block.copy()

        # `deepcopy()` is required here as the block is nested.
        # A simple `copy()` is shallow, and mutations would still be made
        # to the original dict at nested levels
        headline_block_for_wales = copy.deepcopy(base_headline_block)
        headline_block_for_wales["value"]["geography"] = "Wales"
        headline_block_for_wales["value"]["geography_type"] = "Nation"

        headline_block_for_crawley = copy.deepcopy(base_headline_block)
        headline_block_for_crawley["value"]["geography"] = "Crawley"
        headline_block_for_crawley["value"][
            "geography_type"
        ] = "Lower Tier Local Authority"

        assert headline_block_for_england in all_possible_headline_blocks
        assert headline_block_for_wales in all_possible_headline_blocks
        assert headline_block_for_crawley in all_possible_headline_blocks
