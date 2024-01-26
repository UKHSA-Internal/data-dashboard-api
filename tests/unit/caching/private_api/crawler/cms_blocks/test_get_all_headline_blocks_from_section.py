from caching.private_api.crawler.cms_blocks import CMSBlockParser


class TestCMSBlockParserGetAllHeadlineBlocksFromSection:
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
