from caching.private_api.crawler.cms_blocks import CMSBlockParser


class TestCMSBlockParserGetAllSelectedTopicsFromHeadlineBlocks:
    def test_returns_set_of_correct_topics(
        self, example_headline_cms_block: dict[str, str | dict[str, str]]
    ):
        """
        Given a list of headline blocks
        When `get_all_selected_topics_from_headline_blocks()` is called
            from the `CMSBlockParser` class
        Then a set of the correct topics is returned
        """
        # Given
        headline_blocks = [example_headline_cms_block]

        # When
        topics = CMSBlockParser.get_all_selected_topics_from_headline_blocks(
            headline_blocks=headline_blocks
        )

        # Then
        assert topics == {"COVID-19"}
