import pytest

from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.domain.common.utils import ChartTypes
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


class TestTemplateCOVID19Page:
    @property
    def covid_19(self) -> str:
        return "COVID-19"

    def test_sections_in_body_are_correct_order(self):
        """
        Given a `TopicPage` created with a template for the `covid-19` page
        When the `body` is taken from the page
        Then the correct sections are in place
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When
        body = template_covid_19_page.body

        # Then
        assert len(body) == 5
        cases_section = body[0]
        deaths_section = body[1]
        healthcare_section = body[2]
        testing_section = body[3]
        vaccinations_section = body[4]

        # Check that the 1st item is a `section` type for `Cases`
        assert cases_section.block_type == "section"
        assert cases_section.value["heading"] == "Cases"

        # Check that the 2nd item is a `section` type for `Deaths`
        assert deaths_section.block_type == "section"
        assert deaths_section.value["heading"] == "Deaths"

        # Check that the 3rd item is a `section` type for `Healthcare`
        assert healthcare_section.block_type == "section"
        assert healthcare_section.value["heading"] == "Healthcare"

        # Check that the 4th item is a `section` type for `Testing`
        assert testing_section.block_type == "section"
        assert testing_section.value["heading"] == "Testing"

        # Check that the 5th item is a `section` type for `Vaccinations`
        assert vaccinations_section.block_type == "section"
        assert vaccinations_section.value["heading"] == "Vaccinations"

    def test_cases_section_chart_card(self):
        """
        Given a `TopicPage` created with a template for the `covid-19` page
        When the `body` is taken from the page
        Then the correct chart card is in place
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When
        body = template_covid_19_page.body

        # Then
        cases_section = body[0]
        chart_row_card = cases_section.value["content"][0]
        chart_row_card_value = chart_row_card.value

        # Check that this row only contains the 1 card.
        assert len(chart_row_card_value) == 1

        chart_card_value = chart_row_card_value["columns"][0].value

        # Check the title and body passed to the chart card have been set correctly
        assert chart_card_value["title"] == "Cases by specimen date"
        expected_body = "Number of cases by specimen date (the day the test was taken). Data for the last 5 days, highlighted in grey, is incomplete."
        assert chart_card_value["body"] == expected_body

        # Check that the plot for the chart has been set correctly
        chart_plot_value = chart_card_value["chart"][0].value
        assert chart_plot_value["topic"] == self.covid_19
        assert chart_plot_value["metric"] == "COVID-19_cases_casesByDay"
        assert chart_plot_value["chart_type"] == ChartTypes.bar.value

    def test_is_previewable_returns_false(self):
        """
        Given a `TopicPage` created with a template for the `covid-19` page
        When `is_previewable()` is called
        Then False is returned
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When
        page_is_previewable: bool = template_covid_19_page.is_previewable()

        # Then
        assert not page_is_previewable

    def test_enable_area_selector_returns_false_by_default(self):
        """
        Given a `TopicPage` created with a template for the `covid-19` page
        When the `enable_area_selector` field is called
        Then False is returned
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When
        enable_area_selector_for_page: bool = (
            template_covid_19_page.enable_area_selector
        )

        # Then
        assert not enable_area_selector_for_page

    def test_selected_topics_for_covid_template_page(self):
        """
        Given a `TopicPage` created with a template for the `COVID-19` page
        When the `selected_topics` property is called
        Then a set containing the selected topics is returned
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When
        selected_topics: bool = template_covid_19_page.selected_topics

        # Then
        assert selected_topics == {"COVID-19"}

    @pytest.mark.parametrize("enable_area_selector", [True, False])
    def test_is_valid_for_area_selector_for_covid_template_page(
        self, enable_area_selector: bool
    ):
        """
        Given a `TopicPage` created with a template for the `COVID-19` page
        And the `enable_area_selector` field switched on or off
        When the `is_valid_for_area_selector` property is called
        Then the correct boolean is returned
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )
        template_covid_19_page.enable_area_selector = enable_area_selector

        # When
        is_valid_for_area_selector: bool = (
            template_covid_19_page.is_valid_for_area_selector
        )

        # Then
        assert is_valid_for_area_selector == enable_area_selector

    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "page_description",
            "body",
            "related_links_layout",
            "related_links",
            "last_published_at",
            "seo_title",
            "search_description",
            "enable_area_selector",
            "selected_topics",
        ],
    )
    def test_api_fields(self, expected_api_field: str):
        """
        Given an expected API field
        When the `api_fields` attribute is accessed
        Then the field is in the returned list
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # Then
        api_fields = template_covid_19_page.api_fields
        api_field_names: list[str] = [api_field.name for api_field in api_fields]

        assert expected_api_field in api_field_names

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "date_posted",
            "enable_area_selector",
            "page_description",
            "body",
        ],
    )
    def test_content_panels(self, expected_content_panel_name: str):
        """
        Given an expected content panel
        When the `content_panels` attribute is accessed
        Then the field is in the returned list
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # Then
        content_panels = template_covid_19_page.content_panels
        content_panel_names: list[str] = [
            content_panel.field_name for content_panel in content_panels
        ]

        assert expected_content_panel_name in content_panel_names


class TestTemplateInfluenzaPage:
    @property
    def influenza(self) -> str:
        return "Influenza"

    @property
    def influenza_testing_positivity_by_week(self) -> str:
        return "influenza_testing_positivityByWeek"

    @staticmethod
    def _retrieve_nested_chart_block(body):
        testing_section = body[1]
        chart_row_card = testing_section.value["content"][0]
        chart_row_card_value = chart_row_card.value

        chart_card = chart_row_card_value["columns"][1]
        chart_card_value = chart_card.value

        return chart_card_value["chart"]

    def test_first_line_plot_on_multiple_plot_chart_is_placed_correctly(self):
        """
        Given a `TopicPage` created with a template for the `influenza` page
        When the `body` is taken from the page
        Then the 1st plot on the multiple line plot chart has been set correctly
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        body = template_influenza_page.body

        # Then
        chart = self._retrieve_nested_chart_block(body=body)

        plot_0_4_years_value = chart[0].value
        assert plot_0_4_years_value["topic"] == self.influenza
        assert (
            plot_0_4_years_value["metric"] == self.influenza_testing_positivity_by_week
        )
        assert (
            plot_0_4_years_value["chart_type"] == ChartTypes.line_multi_coloured.value
        )
        assert plot_0_4_years_value["age"] == "00-04"
        assert plot_0_4_years_value["label"] == "0 to 4 years"
        assert (
            plot_0_4_years_value["line_colour"]
            == RGBAChartLineColours.COLOUR_1_DARK_BLUE.name
        )
        assert plot_0_4_years_value["line_type"] == ChartLineTypes.SOLID.name

    def test_second_line_plot_on_multiple_plot_chart_is_placed_correctly(self):
        """
        Given a `TopicPage` created with a template for the `influenza` page
        When the `body` is taken from the page
        Then the 2nd plot on the multiple line plot chart has been set correctly
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        body = template_influenza_page.body

        # Then
        chart = self._retrieve_nested_chart_block(body=body)

        plot_5_14_years_value = chart[1].value
        assert plot_5_14_years_value["topic"] == self.influenza
        assert (
            plot_5_14_years_value["metric"] == self.influenza_testing_positivity_by_week
        )
        assert (
            plot_5_14_years_value["chart_type"] == ChartTypes.line_multi_coloured.value
        )
        assert plot_5_14_years_value["age"] == "05-14"
        assert plot_5_14_years_value["label"] == "5 to 14 years"
        assert (
            plot_5_14_years_value["line_colour"]
            == RGBAChartLineColours.COLOUR_2_TURQUOISE.name
        )
        assert plot_5_14_years_value["line_type"] == ChartLineTypes.SOLID.name

    def test_third_line_plot_on_multiple_plot_chart_is_placed_correctly(self):
        """
        Given a `TopicPage` created with a template for the `influenza` page
        When the `body` is taken from the page
        Then the 3rd plot on the multiple line plot chart has been set correctly
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        body = template_influenza_page.body

        # Then
        chart = self._retrieve_nested_chart_block(body=body)

        plot_15_44_years_value = chart[2].value
        assert plot_15_44_years_value["topic"] == self.influenza
        assert (
            plot_15_44_years_value["metric"]
            == self.influenza_testing_positivity_by_week
        )
        assert (
            plot_15_44_years_value["chart_type"] == ChartTypes.line_multi_coloured.value
        )
        assert plot_15_44_years_value["age"] == "15-44"
        assert plot_15_44_years_value["label"] == "15 to 44 years"
        assert (
            plot_15_44_years_value["line_colour"]
            == RGBAChartLineColours.COLOUR_3_DARK_PINK.name
        )
        assert plot_15_44_years_value["line_type"] == ChartLineTypes.SOLID.name

    def test_fourth_line_plot_on_multiple_plot_chart_is_placed_correctly(self):
        """
        Given a `TopicPage` created with a template for the `influenza` page
        When the `body` is taken from the page
        Then the 4th plot on the multiple line plot chart has been set correctly
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        body = template_influenza_page.body

        # Then
        chart = self._retrieve_nested_chart_block(body=body)

        plot_45_64_years_value = chart[3].value
        assert plot_45_64_years_value["topic"] == self.influenza
        assert (
            plot_45_64_years_value["metric"]
            == self.influenza_testing_positivity_by_week
        )
        assert (
            plot_45_64_years_value["chart_type"] == ChartTypes.line_multi_coloured.value
        )
        assert plot_45_64_years_value["age"] == "45-64"
        assert plot_45_64_years_value["label"] == "45 to 64 years"
        assert (
            plot_45_64_years_value["line_colour"]
            == RGBAChartLineColours.COLOUR_4_ORANGE.name
        )
        assert plot_45_64_years_value["line_type"] == ChartLineTypes.SOLID.name

    def test_fifth_line_plot_on_multiple_plot_chart_is_placed_correctly(self):
        """
        Given a `TopicPage` created with a template for the `influenza` page
        When the `body` is taken from the page
        Then the 5th plot on the multiple line plot chart has been set correctly
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        body = template_influenza_page.body

        # Then
        chart = self._retrieve_nested_chart_block(body=body)

        plot_65_plus_years_value = chart[4].value
        assert plot_65_plus_years_value["topic"] == self.influenza
        assert (
            plot_65_plus_years_value["metric"]
            == self.influenza_testing_positivity_by_week
        )
        assert (
            plot_65_plus_years_value["chart_type"]
            == ChartTypes.line_multi_coloured.value
        )
        assert plot_65_plus_years_value["age"] == "65+"
        assert plot_65_plus_years_value["label"] == "65 years and over"
        assert (
            plot_65_plus_years_value["line_colour"]
            == RGBAChartLineColours.COLOUR_5_DARK_GREY.name
        )
        assert plot_65_plus_years_value["line_type"] == ChartLineTypes.SOLID.name

    def test_selected_topics_for_influenza_template_page(self):
        """
        Given a `TopicPage` created with a template for the `Influenza` page
        When the `selected_topics` property is called
        Then a set containing the selected topics is returned
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        selected_topics: bool = template_influenza_page.selected_topics

        # Then
        assert selected_topics == {"Influenza"}


class TestTemplateOtherRespiratoryVirusesPage:
    @pytest.mark.parametrize("enable_area_selector", [True, False])
    def test_is_valid_for_area_selector_returns_false_due_to_multiple_selected_topics(
        self, enable_area_selector: bool
    ):
        """
        Given a `TopicPage` created with a template
            for the `Other Respiratory Viruses` page
        And the `enable_area_selector` field switched on or off
        When the `is_valid_for_area_selector` property is called
        Then False is returned because of the
            multiple selected topics on the page
        """
        # Given
        template_other_respiratory_viruses_page = (
            FakeTopicPageFactory.build_other_respiratory_viruses_page_from_template()
        )
        template_other_respiratory_viruses_page.enable_area_selector = (
            enable_area_selector
        )

        # When
        is_valid_for_area_selector: bool = (
            template_other_respiratory_viruses_page.is_valid_for_area_selector
        )

        # Then
        assert not is_valid_for_area_selector
