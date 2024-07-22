from unittest import mock

import pytest
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.admin.panels.inline_panel import InlinePanel
from wagtail.api.conf import APIField

from cms.dashboard.models import UKHSAPage
from metrics.domain.common.utils import ChartTypes
from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory


class TestBlankHomePage:
    @pytest.mark.parametrize(
        "expected_api_field_name",
        [
            "page_description",
            "body",
            "related_links",
            "last_published_at",
            "seo_title",
            "search_description",
        ],
    )
    def test_has_correct_api_fields(
        self,
        expected_api_field_name: str,
    ):
        """
        Given a blank `HomePage` model
        When `api_fields` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        api_fields: list[APIField] = blank_page.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field_name in api_field_names

    @pytest.mark.parametrize(
        "expected_content_panel_name",
        [
            "title",
            "page_description",
            "body",
        ],
    )
    def test_has_correct_content_panels(
        self,
        expected_content_panel_name: str,
    ):
        """
        Given a blank `HomePage` model
        When `content_panels` is called
        Then the expected names are on the returned `FieldPanel` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        content_panels: list[FieldPanel] = blank_page.content_panels

        # Then
        content_panel_names: set[str] = {p.field_name for p in content_panels}
        assert expected_content_panel_name in content_panel_names

    def test_has_correct_sidebar_panels(self):
        """
        Given a blank `HomePage` model
        When `sidebar_content_panels` is called
        Then the expected names are on the returned `InlinePanel` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        sidebar_content_panels: list[InlinePanel] = blank_page.sidebar_content_panels

        # Then
        expected_sidebar_content_panel_names: set[str] = {
            "related_links",
        }
        sidebar_content_panel_names: set[str] = {
            p.relation_name for p in sidebar_content_panels
        }
        assert sidebar_content_panel_names == expected_sidebar_content_panel_names

    def test_is_previewable_returns_false(self):
        """
        Given a blank `HomePage` model
        When `is_previewable()` is called
        Then False is returned
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        page_is_previewable: bool = blank_page.is_previewable()

        # Then
        assert not page_is_previewable

    @mock.patch.object(UKHSAPage, "get_url_parts")
    def test_get_url_parts(self, mocked_super_get_url_parts: mock.MagicMock):
        """
        Given a `HomePage` model
        When `get_url_parts()` is called
        Then the url parts are returned with
            an empty string representing the page path
        """
        # Given
        expected_site_id = 123
        root_url = "https://my-prefix.dev.ukhsa-data-dashboard.gov.uk"
        page_path = "topics"
        mocked_super_get_url_parts.return_value = (expected_site_id, root_url, page_path)
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        url_parts: tuple[int, str, str] = blank_page.get_url_parts(
            request=mock.Mock()
        )

        # Then
        assert url_parts[0] == expected_site_id
        assert url_parts[1] == root_url
        assert url_parts[2] == "" != page_path


class TestTemplateHomePage:
    @property
    def expected_trend_number_block_body(self) -> str:
        return "7 days"

    @property
    def covid_19(self) -> str:
        return "COVID-19"

    def test_sections_in_body_are_correct_order(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the correct sections are in place
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        assert len(body) == 2
        covid_section, influenza_section = body

        # Check that the first item is a `section` type for `COVID-19`
        assert covid_section.block_type == "section"
        assert covid_section.value["heading"] == "COVID-19"

        # Check that the second item is a `section` type for `Influenza`
        assert influenza_section.block_type == "section"
        assert influenza_section.value["heading"] == "Influenza"

    def test_covid_19_section_text_card(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the first row card in the coronavirus section is the expected text card
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]

        # Check the initial text card is set up correctly
        text_card = covid_content_section[0]
        assert text_card.block_type == "text_card"
        assert "Summary of COVID-19 data." in text_card.value["body"].source

    def test_covid_19_section_headline_number_row_card(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the second row card in the coronavirus section
            is the expected headline numbers row card
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]

        # Check the headline numbers row card is set up correctly
        headline_numbers_row_card = covid_content_section[1]
        assert headline_numbers_row_card.block_type == "headline_numbers_row_card"

        headline_number_row_columns = headline_numbers_row_card.value["columns"]
        assert len(headline_number_row_columns) == 5

    def test_covid_19_section_headline_number_row_headline_and_trend_column(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 1st column component which is a headline and trend component
            in the headline numbers row card within the coronavirus section
            is being set correctly
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        first_column_component = headline_number_row_columns[0].value
        # Check that the title of the component is correct
        assert first_column_component["title"] == "Cases"

        # This column has a headline block and trend block
        # Check that the headline_number block has the correct params
        first_column_headline_block_value = first_column_component["rows"][0].value
        assert first_column_headline_block_value["topic"] == self.covid_19
        assert (
            first_column_headline_block_value["metric"]
            == "COVID-19_headline_cases_7DayTotals"
        )
        assert first_column_headline_block_value["body"] == "Weekly"

        # Check that the trend_number block has the correct params
        first_column_trend_block_value = first_column_component["rows"][1].value
        assert first_column_trend_block_value["topic"] == self.covid_19
        assert (
            first_column_trend_block_value["metric"]
            == "COVID-19_headline_cases_7DayChange"
        )
        assert (
            first_column_trend_block_value["percentage_metric"]
            == "COVID-19_headline_cases_7DayPercentChange"
        )
        assert (
            first_column_trend_block_value["body"]
            == self.expected_trend_number_block_body
        )

    def test_covid_19_section_headline_number_row_headline_and_percentage_blocks(
        self,
    ):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 4th column component which has headline and percentage number blocks
            in the headline numbers row card within the coronavirus section
            is being set correctly
        """
        # Given
        example_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = example_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        fourth_column_component = headline_number_row_columns[3].value
        assert fourth_column_component["title"] == "Vaccines"

        # This is column component which has a headline number block at the top
        fourth_column_headline_block_value = fourth_column_component["rows"][0].value
        assert fourth_column_headline_block_value["topic"] == self.covid_19
        assert (
            fourth_column_headline_block_value["metric"]
            == "COVID-19_headline_vaccines_spring23Total"
        )
        assert fourth_column_headline_block_value["body"] == "Spring booster"

    def test_covid_19_section_headline_number_row_single_headline_column_with_percentage_block(
        self,
    ):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 5th column component which is a percentage block as 1 row of a column
            in the headline numbers row card within the coronavirus section
            is being set correctly
        """
        # Given
        example_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = example_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        # Note that this column component only has the 1 percentage number component
        # Check that the percentage block has the correct params
        fifth_column_value = headline_number_row_columns[4].value
        assert fifth_column_value["title"] == "Testing"
        assert fifth_column_value["rows"][0].block_type == "percentage_number"
        fifth_column_percentage_block_value = fifth_column_value["rows"][0].value
        assert fifth_column_percentage_block_value["topic"] == self.covid_19
        assert (
            fifth_column_percentage_block_value["metric"]
            == "COVID-19_headline_positivity_latest"
        )
        assert fifth_column_percentage_block_value["body"] == "Virus tests positivity"

    def test_covid_19_section_chart_row_card(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the third row card in the coronavirus section is the expected chart row card
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]

        # Check the chart row card is set up correctly
        chart_row_card = covid_content_section[2]
        assert chart_row_card.block_type == "chart_row_card"
        chart_card_columns = chart_row_card.value["columns"]

        assert len(chart_card_columns) == 2

    def test_covid_19_section_chart_card_plot(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the chart plot for the chart card with headline and trend number
            in the charts row card within the coronavirus section
            is being set correctly
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        chart_card_columns = covid_content_section[2].value["columns"]

        chart_with_headline_and_trend_card_value = chart_card_columns[0].value
        assert chart_with_headline_and_trend_card_value["title"] == "Cases"
        assert (
            chart_with_headline_and_trend_card_value["body"]
            == "Positive COVID-19 cases reported in England (7-day rolling average)"
        )

        chart = chart_with_headline_and_trend_card_value["chart"]
        chart_plot_value = chart[0].value
        assert chart_plot_value["topic"] == self.covid_19
        assert chart_plot_value["metric"] == "COVID-19_cases_countRollingMean"
        assert chart_plot_value["chart_type"] == ChartTypes.line_multi_coloured.value

    def test_covid_19_section_chart_card_headline_and_trend_number(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the headline and trend number blocks for the chart card with headline and trend number
            in the charts row card within the coronavirus section
            is being set correctly
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        chart_card_columns = covid_content_section[2].value["columns"]
        chart_with_headline_and_trend_card_value = chart_card_columns[0].value

        headline_number_columns = chart_with_headline_and_trend_card_value[
            "headline_number_columns"
        ]

        headline_number_block_value = headline_number_columns[0].value
        assert headline_number_block_value["topic"] == self.covid_19
        assert (
            headline_number_block_value["metric"]
            == "COVID-19_headline_cases_7DayTotals"
        )
        assert (
            headline_number_block_value["body"] == self.expected_trend_number_block_body
        )

        trend_number_block_value = headline_number_columns[1].value
        assert trend_number_block_value["topic"] == self.covid_19
        assert (
            trend_number_block_value["metric"] == "COVID-19_headline_cases_7DayChange"
        )
        assert (
            trend_number_block_value["percentage_metric"]
            == "COVID-19_headline_cases_7DayPercentChange"
        )
        assert trend_number_block_value["body"] == ""
