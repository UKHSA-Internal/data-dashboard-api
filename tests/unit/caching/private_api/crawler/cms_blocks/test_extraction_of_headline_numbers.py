from caching.private_api.crawler.cms_blocks import CMSBlockParser


class TestCMSBlockParseExtractionOfHeadlineNumbers:
    def test_get_all_headline_blocks_from_section(
        self, example_section_with_headline_chart_and_text_cards
    ):
        """
        Given a section containing headline blocks
            in a mixture of headline number row cards
            as well as within chart cards
        When `get_all_headline_blocks_from_section()` is called
            from the `CMSBlockParser` class
        Then the correct headline blocks are returned
        """
        # Given
        section = example_section_with_headline_chart_and_text_cards

        # When
        headline_blocks = CMSBlockParser.get_all_headline_blocks_from_section(
            section=section
        )

        # Then
        expected_headline_blocks = [
            # The 1st content card is a text card, so nothing to extract there
            # The 2nd content card is headline numbers row card with 2 columns
            section["value"]["content"][1]["value"]["columns"][0]["value"]["rows"][0],
            section["value"]["content"][1]["value"]["columns"][0]["value"]["rows"][1],
            section["value"]["content"][1]["value"]["columns"][1]["value"]["rows"][0],
            # The 3rd content card is a chart row card which has 2 chart cards within it
            # The 1st chart card has multiple headline block within it
            section["value"]["content"][2]["value"]["columns"][0]["value"][
                "headline_number_columns"
            ][0],
            section["value"]["content"][2]["value"]["columns"][0]["value"][
                "headline_number_columns"
            ][1],
            # The other chart card contains no headline blocks
        ]
        assert headline_blocks == expected_headline_blocks

    def test_get_headline_blocks_from_chart_blocks(self, example_chart_blocks):
        """
        Given a list of example chart blocks
        When `get_headline_blocks_from_chart_blocks()` is called
            from the `CMSBlockParser` class
        Then the correct headline number blocks are extracted and returned
        """
        # Given
        chart_blocks = example_chart_blocks

        # When
        headline_blocks = CMSBlockParser.get_headline_blocks_from_chart_blocks(
            chart_blocks=chart_blocks
        )

        # Then
        expected_headline_blocks = [
            chart_blocks[0]["headline_number_columns"][0],
            chart_blocks[0]["headline_number_columns"][1],
            chart_blocks[1]["headline_number_columns"][0],
            chart_blocks[1]["headline_number_columns"][1],
        ]
        assert headline_blocks == expected_headline_blocks

    def test_get_headline_blocks_from_chart_blocks_returns_empty_list_for_no_chart_blocks(
        self,
    ):
        """
        Given an empty list of chart blocks
        When `get_headline_blocks_from_chart_blocks()` is called
            from the `CMSBlockParser` class
        Then an empty list is returned
        """
        # Given
        no_chart_blocks = []

        # When
        headline_number_blocks = CMSBlockParser.get_headline_blocks_from_chart_blocks(
            chart_blocks=no_chart_blocks
        )

        # Then
        assert headline_number_blocks == []
