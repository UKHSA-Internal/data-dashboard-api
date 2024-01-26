from caching.private_api.crawler.cms_blocks import CMSBlockParser


class TestCMSBlockParserGetAllSelectedTopicsFromChartBlocks:
    def test_returns_set_of_correct_topics(
        self, example_chart_block: dict[str, str | list[dict]]
    ):
        """
        Given a list of chart blocks
        When `get_all_selected_topics_from_chart_blocks()` is called
            from the `CMSBlockParser` class
        Then a set of the correct topics is returned
        """
        # Given
        chart_blocks = [example_chart_block]

        # When
        topics = CMSBlockParser.get_all_selected_topics_from_chart_blocks(
            chart_blocks=chart_blocks
        )

        # Then
        assert topics == {"COVID-19"}
