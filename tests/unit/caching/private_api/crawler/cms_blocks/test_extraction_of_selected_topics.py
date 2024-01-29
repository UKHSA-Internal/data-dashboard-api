from caching.private_api.crawler.cms_blocks import CMSBlockParser
from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


class TestCMSBlockParserExtractionOfSelectedTopics:
    def test_get_all_selected_topics_from_chart_blocks(
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

    def test_get_all_selected_topics_from_headline_blocks(
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

    def test_get_all_selected_topics_from_sections(
        self,
        example_section_with_headline_chart_and_text_cards: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a list of section CMS components
        When `get_all_selected_topics_from_sections()` is called
            from the `CMSBlockParser` class
        Then a set containing only the selected topic
            i.e. COVID-19 is returned
        """
        # Given
        sections = [example_section_with_headline_chart_and_text_cards]

        # When
        topics = CMSBlockParser.get_all_selected_topics_from_sections(sections=sections)

        # Then
        assert topics == {"COVID-19"}
