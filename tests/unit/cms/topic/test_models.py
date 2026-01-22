import datetime
from unittest import mock

import pytest

from cms.topic.models import TopicPage
from metrics.domain.charts.colour_scheme import RGBAChartLineColours

from metrics.domain.charts.common_charts.plots.line_multi_coloured.properties import (
    ChartLineTypes,
)
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
        assert len(body) == 6
        headlines_section = body[0]
        cases_section = body[1]
        deaths_section = body[2]
        healthcare_section = body[3]
        testing_section = body[4]
        vaccinations_section = body[5]

        # Check that the 1st item is a `section` type for `Headlines`
        assert headlines_section.block_type == "section"
        assert headlines_section.value["heading"] == "Headlines"

        # Check that the 2nd item is a `section` type for `Cases`
        assert cases_section.block_type == "section"
        assert cases_section.value["heading"] == "Cases"

        # Check that the 3rd item is a `section` type for `Deaths`
        assert deaths_section.block_type == "section"
        assert deaths_section.value["heading"] == "Deaths"

        # Check that the 4th item is a `section` type for `Healthcare`
        assert healthcare_section.block_type == "section"
        assert healthcare_section.value["heading"] == "Healthcare"

        # Check that the 5th item is a `section` type for `Testing`
        assert testing_section.block_type == "section"
        assert testing_section.value["heading"] == "Testing"

        # Check that the 6th item is a `section` type for `Vaccinations`
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
        cases_section = body[1]
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

    @pytest.mark.parametrize("is_public", [True, False])
    def test_is_page_public_selector_for_covid_template_page(self, is_public: bool):
        """
        Given a `TopicPage` created with a template for the `COVID-19` page
        And the is_public` field switched on or off
        When the `is_page_public_selector` property is called
        Then the correct boolean is returned
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )
        template_covid_19_page.is_public = is_public

        # When
        is_page_public_selector: bool = template_covid_19_page.is_page_public_selector

        # Then
        assert is_page_public_selector == is_public

    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "page_description",
            "body",
            "related_links_layout",
            "related_links",
            "last_updated_at",
            "last_published_at",
            "seo_title",
            "search_description",
            "enable_area_selector",
            "is_public",
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
            "enable_area_selector",
            "is_public",
            "page_description",
            "body",
        ],
    )
    def test_content_panels(self, expected_content_panel_name: str):
        """
        Given an expected content panel
        When the attribute is accessed
        Then the panel value can be accessed from the page model
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When / Then
        assert hasattr(template_covid_19_page, expected_content_panel_name)

    def test_find_latest_released_embargo_for_metrics(self):
        """
        Given an instance of a `TopicPage`
        When `find_latest_released_embargo_for_metrics()` is called
        Then the call is delegated to the `CoreTimeSeriesManager`
            and the `CoreHeadlineManager` to fetch
            the latest released embargo timestamp
        """
        # Given
        spy_core_timeseries_manager = mock.Mock()
        spy_core_headline_manager = mock.Mock()

        page = TopicPage(
            core_timeseries_manager=spy_core_timeseries_manager,
            core_headline_manager=spy_core_headline_manager,
            content_type_id=1,
        )

        # When
        latest_released_embargoes = page.find_latest_released_embargo_for_metrics()

        # Then
        spy_core_timeseries_manager.find_latest_released_embargo_for_metrics.assert_called_once_with(
            metrics=page.selected_metrics
        )
        spy_core_headline_manager.find_latest_released_embargo_for_metrics.assert_called_once_with(
            metrics=page.selected_metrics
        )
        assert (
            spy_core_timeseries_manager.find_latest_released_embargo_for_metrics.return_value
            in latest_released_embargoes
        )
        assert (
            spy_core_headline_manager.find_latest_released_embargo_for_metrics.return_value
            in latest_released_embargoes
        )

    def test_selected_metrics(self):
        """
        Given a `TopicPage` created
            with a template for the `COVID-19` page
        When the `selected_metrics` property is called
        Then the correct metrics are extracted
        """
        # Given
        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )

        # When
        selected_metrics: set[str] = template_covid_19_page.selected_metrics

        # Then
        expected_metrics = {
            "COVID-19_cases_casesByDay",
            "COVID-19_cases_countRollingMean",
            "COVID-19_cases_rateRollingMean",
            "COVID-19_deaths_ONSByDay",
            "COVID-19_deaths_ONSRollingMean",
            "COVID-19_healthcare_admissionByDay",
            "COVID-19_healthcare_occupiedBedsByDay",
            "COVID-19_testing_PCRcountByDay",
            "COVID-19_testing_positivity7DayRolling",
            "COVID-19_vaccinations_autumn22_dosesByDay",
            "COVID-19_vaccinations_autumn22_uptakeByDay",
            "COVID-19_vaccinations_spring23_dosesByDay",
            "COVID-19_vaccinations_spring23_uptakeByDay",
            "COVID-19_headline_7DayAdmissions",
            "COVID-19_headline_7DayAdmissionsChange",
            "COVID-19_headline_ONSdeaths_7DayChange",
            "COVID-19_headline_ONSdeaths_7DayTotals",
            "COVID-19_headline_cases_7DayChange",
            "COVID-19_headline_cases_7DayTotals",
            "COVID-19_headline_positivity_latest",
            "COVID-19_headline_vaccines_autumn23Uptake",
        }
        assert selected_metrics == expected_metrics

    @mock.patch.object(TopicPage, "find_latest_released_embargo_for_metrics")
    def test_last_updated_at(
        self, mocked_find_latest_released_embargo_for_metrics: mock.MagicMock
    ):
        """
        Given an embargoed timestamp which is more recent
        And a `last_published_at` timestamp which is older
        When the `last_published_at` property
            is called from an instance of a `TopicPage`
        Then the more recent timestamp is returned
        """
        # Given
        expected_timestamp = datetime.datetime(
            year=2024, month=2, day=2, hour=2, minute=2, second=2
        )
        latest_released_embargoes = [expected_timestamp, None]
        mocked_find_latest_released_embargo_for_metrics.return_value = (
            latest_released_embargoes
        )
        older_timestamp = datetime.datetime(
            year=2024, month=1, day=1, hour=1, minute=1, second=1
        )

        template_covid_19_page = (
            FakeTopicPageFactory.build_covid_19_page_from_template()
        )
        template_covid_19_page.last_published_at = older_timestamp

        # When
        calculated_last_updated_at = template_covid_19_page.last_updated_at

        # Then
        assert calculated_last_updated_at == expected_timestamp


class TestTemplateInfluenzaPage:
    @property
    def influenza(self) -> str:
        return "Influenza"

    @property
    def influenza_testing_positivity_by_week(self) -> str:
        return "influenza_testing_positivityByWeek"

    @staticmethod
    def _retrieve_nested_chart_block(body):
        testing_section = body[2]
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

    def test_selected_metrics(self):
        """
        Given a `TopicPage` created
            with a template for the `Influenza` page
        When the `selected_metrics` property is called
        Then the correct metrics are extracted
        """
        # Given
        template_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )

        # When
        selected_metrics: set[str] = template_influenza_page.selected_metrics

        # Then
        expected_metrics = {
            "influenza_healthcare_ICUHDUadmissionRateByWeek",
            "influenza_testing_positivityByWeek",
            "influenza_headline_ICUHDUadmissionRateChange",
            "influenza_headline_ICUHDUadmissionRateLatest",
            "influenza_headline_positivityLatest",
        }
        assert selected_metrics == expected_metrics


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

    def test_selected_metrics(self):
        """
        Given a `TopicPage` created with a template
            for the `Other Respiratory Viruses` page
        When the `selected_metrics` property is called
        Then the correct metrics are extracted
        """
        # Given
        template_other_respiratory_viruses_page = (
            FakeTopicPageFactory.build_other_respiratory_viruses_page_from_template()
        )

        # When
        selected_metrics: set[str] = (
            template_other_respiratory_viruses_page.selected_metrics
        )

        # Then
        expected_metrics = {
            "RSV_healthcare_admissionRateByWeek",
            "RSV_testing_positivityByWeek",
            "adenovirus_testing_positivityByWeek",
            "hMPV_testing_positivityByWeek",
            "parainfluenza_testing_positivityByWeek",
            "rhinovirus_testing_positivityByWeek",
            "adenovirus_headline_positivityLatest",
            "hMPV_headline_positivityLatest",
            "parainfluenza_headline_positivityLatest",
            "rhinovirus_headline_positivityLatest",
        }
        assert selected_metrics == expected_metrics
