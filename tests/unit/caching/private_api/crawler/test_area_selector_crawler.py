from unittest import mock

from caching.private_api.crawler.area_selector_crawler import AreaSelectorCrawler

EXAMPLE_HEADLINE_NUMBER_BLOCK = {
    "type": "headline_number",
    "value": {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_cases_7DayTotals",
        "geography": "England",
        "geography_type": "Nation",
        "sex": "all",
        "age": "all",
        "stratum": "default",
        "body": "Weekly",
    },
    "id": "eff08341-7bfa-4a3b-b013-527e7b954ce8",
}


EXAMPLE_AVAILABLE_GEOGRAPHIES = {
    "Nation": ["England"],
    "Lower Tier Local Authority": ["Birmingham", "Liverpool"],
}


class TestAreaSelectorCrawler:
    def test_build_all_content_block_combinations(self):
        """
        Given a "headline_number" content block
        And a number of available geographies
        When `build_all_content_block_combinations()` is called
            from an instance of the `AreaSelectorCrawler`
        Then the correct content block combinations are returned
        """
        # Given
        content_block = EXAMPLE_HEADLINE_NUMBER_BLOCK
        expected_geographies = EXAMPLE_AVAILABLE_GEOGRAPHIES
        mocked_geographies_api_crawler = mock.Mock()
        mocked_geographies_api_crawler.process_geographies_api.return_value = (
            expected_geographies
        )
        area_selector_crawler = AreaSelectorCrawler(
            dynamic_content_block_crawler=mock.Mock(),
            geographies_api_crawler=mocked_geographies_api_crawler,
        )

        # When
        all_content_block_combinations = (
            area_selector_crawler.build_all_content_block_combinations(
                content_block=content_block
            )
        )

        # Then
        # There should be 3 content blocks, 1 for each available geography
        assert len(all_content_block_combinations) == 3

        # Check that all the common fields remain unchanged
        for block_combination in all_content_block_combinations:
            assert block_combination["type"] == content_block["type"]
            assert block_combination["id"] == content_block["id"]
            assert (
                block_combination["value"]["topic"] == content_block["value"]["topic"]
            )
            assert (
                block_combination["value"]["metric"] == content_block["value"]["metric"]
            )
            assert block_combination["value"]["sex"] == content_block["value"]["sex"]
            assert block_combination["value"]["age"] == content_block["value"]["age"]
            assert (
                block_combination["value"]["stratum"]
                == content_block["value"]["stratum"]
            )
            assert block_combination["value"]["body"] == content_block["value"]["body"]

        # Check that each geography is injected into
        # an individual copy of the content block
        assert all_content_block_combinations[0]["geography_type"] == "Nation"
        assert (
            all_content_block_combinations[0]["geography"]
            == expected_geographies["Nation"][0]
        )

        assert (
            all_content_block_combinations[1]["geography_type"]
            == "Lower Tier Local Authority"
        )
        assert (
            all_content_block_combinations[1]["geography"]
            == expected_geographies["Lower Tier Local Authority"][0]
        )

        assert (
            all_content_block_combinations[2]["geography_type"]
            == "Lower Tier Local Authority"
        )
        assert (
            all_content_block_combinations[2]["geography"]
            == expected_geographies["Lower Tier Local Authority"][1]
        )

    def test_process_any_headline_number_block(self):
        """
        Given a "headline_number" content block
        And a number of available geographies
        When `process_any_headline_number_block()` is called
            from an instance of the `AreaSelectorCrawler`
        Then the correct content block combinations are used
            in calls made to the dynamic content block crawler
        """
        # Given
        content_block = EXAMPLE_HEADLINE_NUMBER_BLOCK
        expected_geographies = EXAMPLE_AVAILABLE_GEOGRAPHIES
        mocked_geographies_api_crawler = mock.Mock()
        mocked_geographies_api_crawler.process_geographies_api.return_value = (
            expected_geographies
        )
        spy_dynamic_content_block_crawler = mock.Mock()
        area_selector_crawler = AreaSelectorCrawler(
            dynamic_content_block_crawler=spy_dynamic_content_block_crawler,
            geographies_api_crawler=mocked_geographies_api_crawler,
        )

        # When
        area_selector_crawler.process_any_headline_number_block(
            headline_number_block=content_block
        )

        # Then
        england_combo = EXAMPLE_HEADLINE_NUMBER_BLOCK.copy()
        england_combo["geography_type"] = "Nation"
        england_combo["geography"] = "England"

        birmingham_combo = EXAMPLE_HEADLINE_NUMBER_BLOCK.copy()
        birmingham_combo["geography_type"] = "Lower Tier Local Authority"
        birmingham_combo["geography"] = "Birmingham"

        liverpool_combo = EXAMPLE_HEADLINE_NUMBER_BLOCK.copy()
        liverpool_combo["geography_type"] = "Lower Tier Local Authority"
        liverpool_combo["geography"] = "Liverpool"

        expected_calls = [
            mock.call(headline_number_block=block)
            for block in (england_combo, birmingham_combo, liverpool_combo)
        ]
        spy_dynamic_content_block_crawler.process_any_headline_number_block.assert_has_calls(
            calls=expected_calls
        )
