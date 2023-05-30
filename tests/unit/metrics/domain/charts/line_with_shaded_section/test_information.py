from typing import List

import pytest

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.line_with_shaded_section import information

INCREASING_METRIC_VALUE: int = 10
DECREASING_METRIC_VALUE: int = -10


class TestDetermineLineAndFillColours:
    def test_returns_green_colours_for_decreasing_cases(self):
        """
        Given a `change_in_metric_value` which is decreasing
        And a `metric_name` of "new_cases_daily"
        When `determine_line_and_fill_colours()` is called
        Then a pair of green colours is returned
        """
        # Given
        change_in_metric_value = DECREASING_METRIC_VALUE
        metric_name = "new_cases_daily"

        # When
        line_colour, fill_colour = information.determine_line_and_fill_colours(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric_name,
        )

        # Then
        assert line_colour == colour_scheme.RGBAColours.LS_DARK_GREEN
        assert fill_colour == colour_scheme.RGBAColours.LS_LIGHT_GREEN

    def test_returns_red_colours_for_increasing_cases(self):
        """
        Given a `change_in_metric_value` which is increasing
        And a `metric_name` of "new_cases_daily"
        When `determine_line_and_fill_colours()` is called
        Then a pair of red colours is returned
        """
        # Given
        change_in_metric_value = INCREASING_METRIC_VALUE
        metric_name = "new_cases_daily"

        # When
        line_colour, fill_colour = information.determine_line_and_fill_colours(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric_name,
        )

        # Then
        assert line_colour == colour_scheme.RGBAColours.DARK_RED
        assert fill_colour == colour_scheme.RGBAColours.LIGHT_RED


CASES_METRIC_TYPES: List[str] = [
    "new_cases_7days_sum",
    "new_cases_7days_change",
    "new_cases_7days_change_percentage",
    "new_cases_daily",
    "new_cases_rolling_rate_by_age",
    "cases_age_sex",
    "cases_rate_age_sex",
]


class TestIsMetricImprovingForCasesTypeMetrics:
    @pytest.mark.parametrize("metric_name", CASES_METRIC_TYPES)
    def test_cases_type_metrics_going_up_returns_false(self, metric_name: str):
        """
        Given a cases type metric
        And a `change_in_metric_value` which is increasing
        When `is_metric_improving()` is called
        Then False is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = INCREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert not metric_is_improving

    @pytest.mark.parametrize("metric_name", CASES_METRIC_TYPES)
    def test_cases_type_metrics_going_down_returns_true(self, metric_name: str):
        """
        Given a cases type metric
        And a `change_in_metric_value` which is decreasing
        When `is_metric_improving()` is called
        Then True is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = DECREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert metric_is_improving


DEATHS_METRIC_TYPES: List[str] = [
    "new_deaths_7days_sum",
    "new_deaths_7days_change",
    "new_deaths_7days_change_percentage",
    "new_deaths_daily_cases_rolling_rate_by_age",
]


class TestIsMetricImprovingForDeathTypeMetrics:
    @pytest.mark.parametrize("metric_name", DEATHS_METRIC_TYPES)
    def test_deaths_type_metrics_going_up_returns_false(self, metric_name: str):
        """
        Given a deaths type metric
        And a `change_in_metric_value` which is increasing
        When `is_metric_improving()` is called
        Then False is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = INCREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert not metric_is_improving

    @pytest.mark.parametrize("metric_name", DEATHS_METRIC_TYPES)
    def test_deaths_type_metrics_going_down_returns_true(self, metric_name: str):
        """
        Given a deaths type metric
        And a `change_in_metric_value` which is decreasing
        When `is_metric_improving()` is called
        Then True is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = DECREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert metric_is_improving


HEALTHCARE_METRIC_TYPES: List[str] = [
    "new_admissions_7days",
    "new_admissions_7days_change",
    "new_admissions_7days_change_percentage",
    "covid_occupied_beds_latest",
    "covid_occupied_mv_beds_latest",
    "new_admissions_daily",
    "admissions_age",
    "admissions_rates_age",
    "covid_occupied_mv_beds",
    "covid_occupied_beds",
]


class TestIsMetricImprovingForHealthcareTypeMetrics:
    @pytest.mark.parametrize("metric_name", HEALTHCARE_METRIC_TYPES)
    def test_healthcare_type_metrics_going_up_returns_false(self, metric_name: str):
        """
        Given a healthcare type metric
        And a `change_in_metric_value` which is increasing
        When `is_metric_improving()` is called
        Then False is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = INCREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert not metric_is_improving

    @pytest.mark.parametrize("metric_name", HEALTHCARE_METRIC_TYPES)
    def test_healthcare_type_metrics_going_down_returns_true(self, metric_name: str):
        """
        Given a healthcare type metric
        And a `change_in_metric_value` which is decreasing
        When `is_metric_improving()` is called
        Then True is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = DECREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert metric_is_improving


TESTING_METRIC_TYPES: List[str] = [
    "new_tests_7days_change",
    "new_tests_7days_change_percentage",
    "unique_individuals_pcr_rolling_sum (bar)",
]


class TestIsMetricImprovingForTestingTypeMetrics:
    @pytest.mark.parametrize("metric_name", TESTING_METRIC_TYPES)
    def test_testing_type_metrics_going_up_returns_true(self, metric_name: str):
        """
        Given a testing type metric
        And a `change_in_metric_value` which is increasing
        When `is_metric_improving()` is called
        Then True is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = INCREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert metric_is_improving

    @pytest.mark.parametrize("metric_name", TESTING_METRIC_TYPES)
    def test_testing_type_metrics_going_down_returns_false(self, metric_name: str):
        """
        Given a testing type metric
        And a `change_in_metric_value` which is decreasing
        When `is_metric_improving()` is called
        Then False is returned
        """
        # Given
        change_in_metric_value = DECREASING_METRIC_VALUE
        metric = metric_name

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert not metric_is_improving

    def test_testing_pcr_positivity_metric_going_up_returns_false(self):
        """
        Given a `positivity_pcr_rolling_sum` metric
        And a `change_in_metric_value` which is increasing
        When `is_metric_improving()` is called
        Then False is returned
        """
        # Given
        change_in_metric_value = INCREASING_METRIC_VALUE
        metric_name = "positivity_pcr_rolling_sum"

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric_name,
        )

        # Then
        assert not metric_is_improving

    def test_testing_pcr_positivity_metric_going_down_returns_true(self):
        """
        Given a `positivity_pcr_rolling_sum` metric
        And a `change_in_metric_value` which is decreasing
        When `is_metric_improving()` is called
        Then True is returned
        """
        # Given
        change_in_metric_value = DECREASING_METRIC_VALUE
        metric_name = "positivity_pcr_rolling_sum"

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric_name,
        )

        # Then
        assert metric_is_improving


VACCINATION_METRIC_TYPES: List[str] = [
    "total_vaccines_given",
    "latest_total_vaccinations_autumn22",
    "latest_vaccination_uptake_autumn22",
    "new_people_vaccinated_autumn22",
    "vaccination_percentage_uptake_autumn22",
    "new_people_vaccinated_spring22",
    "vaccination_percentage_uptake_spring22",
]


class TestIsMetricImprovingForVaccinationTypeMetrics:
    @pytest.mark.parametrize("metric_name", VACCINATION_METRIC_TYPES)
    def test_vaccination_type_metrics_going_up_returns_true(self, metric_name: str):
        """
        Given a vaccination type metric
        And a `change_in_metric_value` which is increasing
        When `is_metric_improving()` is called
        Then True is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = INCREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert metric_is_improving

    @pytest.mark.parametrize("metric_name", VACCINATION_METRIC_TYPES)
    def test_vaccination_type_metrics_going_down_returns_false(self, metric_name: str):
        """
        Given a vaccination type metric
        And a `change_in_metric_value` which is decreasing
        When `is_metric_improving()` is called
        Then False is returned
        """
        # Given
        metric = metric_name
        change_in_metric_value = DECREASING_METRIC_VALUE

        # When
        metric_is_improving: bool = information.is_metric_improving(
            change_in_metric_value=change_in_metric_value,
            metric_name=metric,
        )

        # Then
        assert not metric_is_improving


def test_raises_error_for_unsupported_metric_name():
    """
    Given a metric name which is not supported
    When `is_metric_improving()` is called
    Then a `ValueError` is raised
    """
    # Given
    unsupported_metric_name = "non_existent_metric"

    # When / Then
    with pytest.raises(ValueError):
        information.is_metric_improving(
            change_in_metric_value=10, metric_name=unsupported_metric_name
        )
