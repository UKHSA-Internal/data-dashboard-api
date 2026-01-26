import pytest

from metrics.domain.common import information

INCREASING_METRIC_VALUE: int = 10
DECREASING_METRIC_VALUE: int = -10

CASES_METRIC_TYPES: list[str] = [
    "new_cases_7days_sum",
    "new_cases_7days_change",
    "new_cases_7days_change_percentage",
    "new_cases_daily",
    "new_cases_rolling_rate_by_age",
    "cases_age_sex",
    "cases_rate_age_sex",
    "COVID-19_cases_casesByDay",
    "COVID-19_cases_countRollingMean",
    "COVID-19_cases_rateRollingMean",
    "COVID-19_headline_cases_7DayChange",
    "COVID-19_headline_cases_7DayPercentChange",
    "COVID-19_headline_cases_7DayTotals",
    "RSV_headline_admissionRateLatest",
    "RSV_headline_positivityLatest",
    "adenovirus_headline_positivityLatest",
    "adenovirus_testing_positivityByWeek",
    "hMPV_headline_positivityLatest",
    "hMPV_testing_positivityByWeek",
    "influenza_headline_positivityLatest",
    "influenza_testing_positivityByWeek",
    "parainfluenza_headline_positivityLatest",
    "parainfluenza_testing_positivityByWeek",
    "rhinovirus_headline_positivityLatest",
    "rhinovirus_testing_positivityByWeek",
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


DEATHS_METRIC_TYPES: list[str] = [
    "new_deaths_7days_sum",
    "new_deaths_7days_change",
    "new_deaths_7days_change_percentage",
    "new_deaths_daily_cases_rolling_rate_by_age",
    "COVID-19_deaths_ONSByDay",
    "COVID-19_deaths_ONSByWeek",
    "COVID-19_deaths_ONSRollingMean",
    "COVID-19_headline_ONSdeaths_7DayChange",
    "COVID-19_headline_ONSdeaths_7DayPercentChange",
    "COVID-19_headline_ONSdeaths_7DayTotals",
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


HEALTHCARE_METRIC_TYPES: list[str] = [
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
    "COVID-19_healthcare_admissionByDay",
    "COVID-19_healthcare_admissionRollingMean",
    "COVID-19_healthcare_occupiedBedsRollingMean",
    "COVID-19_healthcare_occupiedBedsByDay",
    "COVID-19_headline_7DayAdmissionsChange",
    "COVID-19_headline_7DayAdmissions",
    "COVID-19_headline_7DayAdmissionsPercentChange",
    "COVID-19_headline_7DayOccupiedBeds",
    "COVID-19_headline_7DayOccupiedBedsChange",
    "COVID-19_headline_7DayOccupiedBedsPercentChange",
    "RSV_headline_admissionRateLatest",
    "RSV_healthcare_admissionRateByWeek",
    "influenza_headline_ICUHDUadmissionRateChange",
    "influenza_headline_ICUHDUadmissionRateLatest",
    "influenza_healthcare_ICUHDUadmissionRateByWeek",
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


TESTING_METRIC_TYPES: list[str] = [
    "new_tests_7days_change",
    "new_tests_7days_change_percentage",
    "unique_individuals_pcr_rolling_sum (bar)",
    "COVID-19_headline_tests_7DayChange",
    "COVID-19_headline_tests_7DayTotals",
    "COVID-19_headline_tests_7DayPercentChange",
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


VACCINATION_METRIC_TYPES: list[str] = [
    "total_vaccines_given",
    "latest_total_vaccinations_autumn22",
    "latest_vaccination_uptake_autumn22",
    "new_people_vaccinated_autumn22",
    "vaccination_percentage_uptake_autumn22",
    "new_people_vaccinated_spring22",
    "vaccination_percentage_uptake_spring22",
    "COVID-19_vaccinations_autumn22_dosesByDay",
    "COVID-19_vaccinations_autumn22_uptakeByDay",
    "COVID-19_vaccinations_spring23_dosesByDay",
    "COVID-19_vaccinations_spring23_uptakeByDay",
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
    Then a `TrendMetricNotSupportedError` is raised
    """
    # Given
    unsupported_metric_name = "non_existent_metric"

    # When / Then
    with pytest.raises(information.TrendMetricNotSupportedError):
        information.is_metric_improving(
            change_in_metric_value=10, metric_name=unsupported_metric_name
        )
