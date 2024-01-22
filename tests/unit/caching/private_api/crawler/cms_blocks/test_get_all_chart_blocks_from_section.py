from caching.private_api.crawler.cms_blocks import CMSBlockParser


class TestCMSBlockParserGetAllChartBlocksFromSection:
    def test_returns_correct_chart_blocks(self, example_section_with_headline_card_and_chart_card):
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
