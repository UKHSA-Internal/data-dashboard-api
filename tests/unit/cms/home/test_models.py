from typing import List, Set

from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.admin.panels.inline_panel import InlinePanel
from wagtail.api.conf import APIField

from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory


class TestBlankHomePage:
    def test_has_correct_api_fields(self):
        """
        Given a blank `HomePage` model
        When `api_fields` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        api_fields: List[APIField] = blank_page.api_fields

        # Then
        expected_api_field_names: Set[str] = {
            "page_description",
            "body",
            "related_links",
            "last_published_at",
        }
        api_field_names: Set[str] = {api_field.name for api_field in api_fields}
        assert api_field_names == expected_api_field_names

    def test_has_correct_content_panels(self):
        """
        Given a blank `HomePage` model
        When `content_panels` is called
        Then the expected names are on the returned `FieldPanel` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        content_panels: List[FieldPanel] = blank_page.content_panels

        # Then
        expected_content_panel_names: Set[str] = {
            "title",
            "page_description",
            "body",
        }
        content_panel_names: Set[str] = {p.field_name for p in content_panels}
        assert content_panel_names == expected_content_panel_names

    def test_has_correct_sidebar_panels(self):
        """
        Given a blank `HomePage` model
        When `sidebar_content_panels` is called
        Then the expected names are on the returned `InlinePanel` objects
        """
        # Given
        blank_page = FakeHomePageFactory.build_blank_page()

        # When
        sidebar_content_panels: List[InlinePanel] = blank_page.sidebar_content_panels

        # Then
        expected_sidebar_content_panel_names: Set[str] = {
            "related_links",
        }
        sidebar_content_panel_names: Set[str] = {
            p.relation_name for p in sidebar_content_panels
        }
        assert sidebar_content_panel_names == expected_sidebar_content_panel_names


class TestTemplateHomePage:
    @property
    def expected_trend_number_block_body(self) -> str:
        return "Last 7 days"

    @property
    def covid_19(self) -> str:
        return "COVID-19"

    def test_stream_blocks_in_body_are_correct_order(self):
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

        # Check that the first item is a `section` type for `Coronavirus`
        assert covid_section.block_type == "section"
        assert covid_section.value["heading"] == "Coronavirus"

        # Check that the second item is a `section` type for `Influenza`
        assert influenza_section.block_type == "section"
        assert influenza_section.value["heading"] == "Influenza"

    def test_coronavirus_section_text_card(self):
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
        assert (
            "The UKHSA dashboard for data and insights on Coronavirus"
            in text_card.value["body"].source
        )

    def test_coronavirus_section_headline_number_row_card(self):
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

    def test_coronavirus_section_headline_number_row_first_column(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 1st column component in the headline numbers row card
            in the coronavirus section is being set correctly
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        first_column_value = headline_number_row_columns[0].value
        # Check that the title of the component is correct
        assert first_column_value["title"] == "Cases"

        # Check that the headline_number block has the correct params
        first_column_headline_block = first_column_value["headline_number"]
        assert first_column_headline_block["topic"] == self.covid_19
        assert first_column_headline_block["metric"] == "new_cases_7days_sum"
        assert first_column_headline_block["body"] == "Weekly"

        # Check that the trend_number block has the correct params
        first_column_trend_block = first_column_value["trend_number"]
        assert first_column_trend_block["topic"] == self.covid_19
        assert first_column_trend_block["metric"] == "new_cases_7days_change"
        assert (
            first_column_trend_block["percentage_metric"]
            == "new_cases_7days_change_percentage"
        )
        assert first_column_trend_block["body"] == self.expected_trend_number_block_body

    def test_coronavirus_section_headline_number_row_second_column(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 2nd column component in the headline numbers row card
            in the coronavirus section is being set correctly
        """
        # Given
        template_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = template_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        second_column_value = headline_number_row_columns[1].value

        assert second_column_value["title"] == "Deaths"

        # Check that the headline_number block has the correct params
        second_column_headline_block = second_column_value["headline_number"]
        assert second_column_headline_block["topic"] == self.covid_19
        assert second_column_headline_block["metric"] == "new_deaths_7days_sum"
        assert second_column_headline_block["body"] == "Weekly"

        # Check that the trend_number block has the correct params
        second_column_trend_block = second_column_value["trend_number"]
        assert second_column_trend_block["topic"] == self.covid_19
        assert second_column_trend_block["metric"] == "new_deaths_7days_change"
        assert (
            second_column_trend_block["percentage_metric"]
            == "new_deaths_7days_change_percentage"
        )
        assert (
            second_column_trend_block["body"] == self.expected_trend_number_block_body
        )

    def test_coronavirus_section_headline_number_row_third_column(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 3rd column component in the headline numbers row card
            in the coronavirus section is being set correctly
        """
        # Given
        example_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = example_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        third_column_value = headline_number_row_columns[2].value
        assert third_column_value["title"] == "Healthcare"

        # Check that the headline_number block has the correct params
        third_column_headline_block = third_column_value["headline_number"]
        assert third_column_headline_block["topic"] == self.covid_19
        assert third_column_headline_block["metric"] == "new_admissions_7days"
        assert third_column_headline_block["body"] == "Patients admitted"

        # Check that the trend_number block has the correct params
        third_column_trend_block = third_column_value["trend_number"]
        assert third_column_trend_block["topic"] == self.covid_19
        assert third_column_trend_block["metric"] == "new_admissions_7days_change"
        assert (
            third_column_trend_block["percentage_metric"]
            == "new_admissions_7days_change_percentage"
        )
        assert third_column_trend_block["body"] == self.expected_trend_number_block_body

    def test_coronavirus_section_headline_number_row_fourth_column(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 4th column component in the headline numbers row card
            in the coronavirus section is being set correctly
        """
        # Given
        example_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = example_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        fourth_column_value = headline_number_row_columns[3].value
        assert fourth_column_value["title"] == "Vaccines"

        # Note that this is a dual headline number component
        # So we expect 2 headline number blocks
        # Check that the top headline_number block has the correct params
        fourth_column_headline_block = fourth_column_value["top_headline_number"]
        assert fourth_column_headline_block["topic"] == self.covid_19
        assert (
            fourth_column_headline_block["metric"]
            == "latest_total_vaccinations_autumn22"
        )
        assert fourth_column_headline_block["body"] == "Autumn booster"

        # Check that the bottom headline_number block has the correct params
        fourth_column_trend_block = fourth_column_value["bottom_headline_number"]
        assert fourth_column_trend_block["topic"] == self.covid_19
        assert (
            fourth_column_trend_block["metric"] == "latest_vaccinations_uptake_autumn22"
        )
        assert fourth_column_trend_block["body"] == "Percentage uptake (%)"

    def test_coronavirus_section_headline_number_row_fifth_column(self):
        """
        Given a `HomePage` created with a template for the `respiratory-viruses` page
        When the `body` is taken from the page
        Then the 5th and last column component in the headline numbers row card
            in the coronavirus section is being set correctly
        """
        # Given
        example_home_page = FakeHomePageFactory.build_home_page_from_template()

        # When
        body = example_home_page.body

        # Then
        covid_section, _ = body
        covid_content_section = covid_section.value["content"]
        headline_number_row_columns = covid_content_section[1].value["columns"]

        # Note that this is a single headline number component
        # Check that the headline_number block has the correct params
        fifth_column_value = headline_number_row_columns[4].value
        assert fifth_column_value["title"] == "Testing"
        fifth_column_headline_block = fifth_column_value["headline_number"]
        assert fifth_column_headline_block["topic"] == self.covid_19
        assert fifth_column_headline_block["metric"] == "positivity_7days_latest"
        assert fifth_column_headline_block["body"] == "Virus tests positivity (%)"

    def test_coronavirus_section_chart_row_card(self):
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
