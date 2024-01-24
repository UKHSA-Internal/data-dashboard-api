import pytest

from caching.private_api.crawler.cms_blocks import CMSBlockParser
from caching.private_api.crawler.geographies_crawler import GeographyData
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


class TestCMSBlockParserGetAllChartBlocksFromSectionForGeography:
    @pytest.mark.parametrize(
        "geography_data",
        [
            GeographyData(
                name="Reading", geography_type_name="Lower Tier Local Authority"
            ),
            GeographyData(name="Wales", geography_type_name="Nation"),
        ],
    )
    def test_returns_correct_chart_blocks_when_geography_data_is_provided(
        self,
        geography_data: GeographyData,
        example_section_with_headline_card_and_chart_card: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a section containing chart blocks within chart cards
        And an enriched `GeographyData` model
        When `get_all_chart_blocks_from_section()` is called
            from the `CMSBlockParser` class
        Then geography information has been injected into
            returned chart blocks
        """
        # Given
        section = example_section_with_headline_card_and_chart_card

        # When
        chart_blocks = CMSBlockParser.get_all_chart_blocks_from_section_for_geography(
            section=section, geography_data=geography_data
        )

        # Then
        # The geography information has been injected into the output
        assert chart_blocks[0]["chart"][0]["value"]["geography"] == geography_data.name
        assert (
            chart_blocks[0]["chart"][0]["value"]["geography_type"]
            == geography_data.geography_type_name
        )
        assert chart_blocks[1]["chart"][0]["value"]["geography"] == geography_data.name
        assert (
            chart_blocks[1]["chart"][0]["value"]["geography_type"]
            == geography_data.geography_type_name
        )

    def test_returns_base_chart_blocks_when_geography_data_not_provided(
        self,
        example_section_with_headline_card_and_chart_card: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a section containing chart blocks within chart cards
        And no `GeographyData` model
        When `get_all_chart_blocks_from_section()` is called
            from the `CMSBlockParser` class
        Then the base chart blocks are returned
        """
        # Given
        section = example_section_with_headline_card_and_chart_card

        # When
        chart_blocks = CMSBlockParser.get_all_chart_blocks_from_section_for_geography(
            section=section, geography_data=None
        )

        # Then
        expected_base_geography = "England"
        expected_base_geography_type = "Nation"

        # The geography information has been injected into the output
        assert (
            chart_blocks[0]["chart"][0]["value"]["geography"] == expected_base_geography
        )
        assert (
            chart_blocks[0]["chart"][0]["value"]["geography_type"]
            == expected_base_geography_type
        )
        assert (
            chart_blocks[1]["chart"][0]["value"]["geography"] == expected_base_geography
        )
        assert (
            chart_blocks[1]["chart"][0]["value"]["geography_type"]
            == expected_base_geography_type
        )
