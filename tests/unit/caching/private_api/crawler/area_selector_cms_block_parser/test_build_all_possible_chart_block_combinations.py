import copy
from unittest import mock

from caching.private_api.crawler.area_selector_cms_block_parser import (
    AreaSelectorCMSBlockParser,
)
from caching.private_api.crawler.geographies_crawler import GeographyTypeData


class TestBuildAllPossibleChartBlockCombinations:
    def test_returns_expected_combinations(self):
        """
        Given a list of enriched `GeographyTypeData` models
            returned from the `process_geographies_api()` method
            on the `GeographyAPICrawler`
        And a base chart block
        When `build_all_possible_chart_block_combinations()` is called
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

        base_chart_block = {
            "title": "Testing",
            "body": "Weekly positivity for influenza",
            "x_axis": "",
            "y_axis": "",
            "chart": [
                {
                    "type": "plot",
                    "value": {
                        "topic": "Influenza",
                        "metric": "influenza_testing_positivityByWeek",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "chart_type": "bar",
                        "date_from": None,
                        "date_to": None,
                        "label": "",
                        "line_colour": "",
                        "line_type": "",
                    },
                    "id": "f1a643ba-ff7e-4118-a0a8-366288468cb0",
                }
            ],
            "headline_number_columns": [],
        }
        area_selector_cms_block_parser = AreaSelectorCMSBlockParser(
            geographies_api_crawler=mocked_geographies_api_crawler
        )

        # When
        all_possible_chart_blocks = (
            area_selector_cms_block_parser.build_all_possible_chart_block_combinations(
                chart_block=base_chart_block
            )
        )

        # Then
        assert len(all_possible_chart_blocks) == 3
        chart_block_for_england = base_chart_block.copy()

        # `deepcopy()` is required here as the block is nested.
        # A simple `copy()` is shallow, and mutations would still be made
        # to the original dict at nested levels
        chart_block_for_wales = copy.deepcopy(base_chart_block)
        chart_block_for_wales["chart"][0]["value"]["geography"] = "Wales"
        chart_block_for_wales["chart"][0]["value"]["geography_type"] = "Nation"

        chart_block_for_crawley = copy.deepcopy(base_chart_block)
        chart_block_for_crawley["chart"][0]["value"]["geography"] = "Crawley"
        chart_block_for_crawley["chart"][0]["value"][
            "geography_type"
        ] = "Lower Tier Local Authority"

        assert chart_block_for_england in all_possible_chart_blocks
        assert chart_block_for_wales in all_possible_chart_blocks
        assert chart_block_for_crawley in all_possible_chart_blocks
