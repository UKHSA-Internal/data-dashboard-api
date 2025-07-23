from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE
from cms.dynamic_content.blocks_deconstruction import CMSBlockParser


class TestCMSBlockParserExtractionOfMetrics:
    def test_get_all_selected_metrics_from_sections(
        self,
        example_section_with_headline_chart_and_text_cards: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a list of section CMS components
        When `get_all_selected_metrics_from_sections()` is called
            from the `CMSBlockParser` class
        Then a set containing only the selected metrics
        """
        # Given
        sections = [example_section_with_headline_chart_and_text_cards]

        # When
        metrics: set[str] = CMSBlockParser.get_all_selected_metrics_from_sections(
            sections=sections
        )

        # Then
        expected_metrics = {
            "COVID-19_cases_countRollingMean",
            "COVID-19_deaths_ONSRollingMean",
            "COVID-19_headline_cases_7DayChange",
            "COVID-19_headline_cases_7DayTotals",
            "COVID-19_headline_positivity_latest",
        }
        assert metrics == expected_metrics

    def test_get_all_selected_metrics_from_sections_for_global_filters(
        self,
        example_section_with_global_filter: CMS_COMPONENT_BLOCK_TYPE,
    ):
        """
        Given a list of section CMS components
            which contain a global filter
        When `get_all_selected_metrics_from_sections()` is called
            from the `CMSBlockParser` class
        Then a set containing only the selected metrics
        """
        # Given
        sections = [example_section_with_global_filter]

        # When
        metrics: set[str] = CMSBlockParser.get_all_selected_metrics_from_sections(
            sections=sections
        )

        # Then
        expected_metrics = {"MMR1_coverage_coverageByYear"}
        assert metrics == expected_metrics
