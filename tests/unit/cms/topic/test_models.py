from metrics.domain.utils import ChartTypes
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory


class TestTemplateCoronavirusPage:
    @property
    def covid_19(self) -> str:
        return "COVID-19"

    def test_sections_in_body_are_correct_order(self):
        """
        Given a `TopicPage` created with a template for the `coronavirus` page
        When the `body` is taken from the page
        Then the correct sections are in place
        """
        # Given
        template_coronavirus_page = (
            FakeTopicPageFactory.build_coronavirus_page_from_template()
        )

        # When
        body = template_coronavirus_page.body

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
        Given a `TopicPage` created with a template for the `coronavirus` page
        When the `body` is taken from the page
        Then the correct chart card is in place
        """
        # Given
        template_home_page = FakeTopicPageFactory.build_coronavirus_page_from_template()

        # When
        body = template_home_page.body

        # Then
        cases_section = body[0]
        chart_row_card = cases_section.value["content"][0]
        chart_row_card_value = chart_row_card.value

        # Check that this row only contains the 1 card.
        assert len(chart_row_card_value) == 1

        chart_card_value = chart_row_card_value["columns"][0].value

        # Check the title and body passed to the chart card have been set correctly
        assert chart_card_value["title"] == "Cases by specimen date"
        expected_body = """Number of cases by specimen date. Data for the last 5 days, highlighted in grey, are incomplete."""
        assert chart_card_value["body"] == expected_body

        # Check that the plot for the chart has been set correctly
        chart_plot_value = chart_card_value["chart"][0].value
        assert chart_plot_value["topic"] == self.covid_19
        assert chart_plot_value["metric"] == "new_cases_daily"
        assert chart_plot_value["chart_type"] == ChartTypes.bar.value
