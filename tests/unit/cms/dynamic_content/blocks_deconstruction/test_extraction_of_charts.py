import pytest

from caching.common.geographies_crawler import GeographyData
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE
from cms.dynamic_content.blocks_deconstruction import CMSBlockParser


class TestCMSBlockParserExtractionOfCharts:
    def test_get_all_chart_blocks_from_section(
        self,
        example_section_with_headline_card_and_chart_card: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a section containing chart blocks within chart cards
        When `get_all_chart_blocks_from_section()` is called
            from the `CMSBlockParser` class
        Then the correct chart blocks are returned
        """
        # Given
        section = example_section_with_headline_card_and_chart_card

        # When
        chart_blocks = CMSBlockParser.get_all_chart_blocks_from_section(section=section)

        # Then
        expected_chart_blocks = [
            # The 1st content card is a headline numbers row card, so nothing to extract there
            section["value"]["content"][1]["value"]["columns"][0]["value"],
            section["value"]["content"][1]["value"]["columns"][1]["value"],
            # The 2nd content card is a chart row card which contains 1 chart in each of the 2 rows.
            # So we expect to extract 2 chart blocks to be extracted
        ]
        assert chart_blocks == expected_chart_blocks

    @pytest.mark.parametrize(
        "geography_data",
        [
            GeographyData(
                name="Reading", geography_type="Lower Tier Local Authority"
            ),
            GeographyData(name="Wales", geography_type="Nation"),
        ],
    )
    def test_get_all_chart_blocks_from_section_for_geography_when_geography_data_is_provided(
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
            == geography_data.geography_type
        )
        assert chart_blocks[1]["chart"][0]["value"]["geography"] == geography_data.name
        assert (
            chart_blocks[1]["chart"][0]["value"]["geography_type"]
            == geography_data.geography_type
        )

    def test_get_all_chart_blocks_from_section_for_geography_when_geography_data_not_provided(
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

    @pytest.mark.parametrize(
        "geography_data",
        [
            GeographyData(
                name="Reading", geography_type="Lower Tier Local Authority"
            ),
            GeographyData(name="Wales", geography_type="Nation"),
        ],
    )
    def test_rebuild_chart_block_for_geography(
        self,
        geography_data: GeographyData,
        example_chart_block: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a chart block and an enriched `GeographyData` model
        When `rebuild_chart_block_for_geography()` is called
            from the `CMSBlockParser` class
        Then a copy of the chart block is returned
            with the geography data injected into the chart plots
        """
        # Given
        base_chart_block = example_chart_block

        # When
        rebuilt_chart_block = CMSBlockParser.rebuild_chart_block_for_geography(
            chart_block=base_chart_block, geography_data=geography_data
        )

        # Then
        assert (
            rebuilt_chart_block["chart"][0]["value"]["geography"] == geography_data.name
        )
        assert (
            rebuilt_chart_block["chart"][0]["value"]["geography_type"]
            == geography_data.geography_type
        )

    def test_get_chart_blocks_from_chart_row_cards(self, example_chart_row_cards):
        """
        Given a list of example chart row cards
        When `get_chart_blocks_from_chart_row_cards()` is called
            from the `CMSBlockParser` class
        Then the correct chart blocks are extracted and returned
        """
        # Given
        chart_row_cards = example_chart_row_cards

        # When
        chart_blocks = CMSBlockParser.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=chart_row_cards
        )

        # Then
        expected_chart_blocks = [
            chart_row_cards[0]["value"]["columns"][0]["value"],
            chart_row_cards[0]["value"]["columns"][1]["value"],
        ]
        assert chart_blocks == expected_chart_blocks

    def test_get_chart_blocks_from_chart_row_cards_returns_empty_list_for_no_cards(
        self,
    ):
        """
        Given an empty list of chart row cards
        When `get_chart_cards_from_chart_row_cards()`
            from the `CMSBlockParser` class
        Then an empty list is returned
        """
        # Given
        no_chart_row_cards = []

        # When
        chart_blocks = CMSBlockParser.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=no_chart_row_cards
        )

        # Then
        assert chart_blocks == []

    def test_get_chart_blocks_from_chart_row_cards_returns_empty_list_for_incorrect_cards(
        self,
    ):
        """
        Given a list of incorrect headline number row cards
        When `get_chart_blocks_from_chart_row_cards()` is called
            from the `CMSBlockParser` class
        Then an empty list is returned
        """
        # Given
        incorrect_chart_cards = [
            {"type": "chart_row_card", "value": {"incorrect_key": []}}
        ]

        # When
        chart_blocks = CMSBlockParser.get_chart_blocks_from_chart_row_cards(
            chart_row_cards=incorrect_chart_cards
        )

        # Then
        assert chart_blocks == []
