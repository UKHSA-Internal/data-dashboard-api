from caching.private_api.crawler.cms_blocks import CMSBlockParser


class TestGetHeadlineBlocksFromChartCards:
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

    def test_get_headline_blocks_from_chart_blocks_returns_empty_list_for_no_chart_blocks(self):
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
