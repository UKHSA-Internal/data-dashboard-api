import datetime

import pytest

from metrics.domain.common.utils import (
    ChartAxisFields,
    ChartTypes,
    _check_for_substring_match,
    DataSourceFileType,
    extract_metric_group_from_metric,
)


class TestChartAxisFields:
    @pytest.mark.parametrize(
        "valid_name",
        [
            "stratum",
            "date",
            "metric",
        ],
    )
    def test_get_x_axis_value_for_valid_name(self, valid_name: str):
        """
        Given a name of an axis type
        When `get_x_axis_value()` is called from the `ChartAxisFields` enum class
        Then the correct value is returned
        """
        # Given
        valid_axis_name = valid_name

        # When
        axis_value = ChartAxisFields.get_x_axis_value(name=valid_axis_name)

        # Then
        assert axis_value == ChartAxisFields[valid_axis_name].value

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",
            "-",
            None,
        ],
    )
    def test_get_x_axis_value_for_invalid_name_returns_default(self, invalid_name: str):
        """
        Given an invalid name for an axis type
        When `get_x_axis_value()` is called from the `ChartAxisFields` enum class
        Then the value of the default of `date` is returned
        """
        # Given
        invalid_axis_name = invalid_name

        # When
        axis_value = ChartAxisFields.get_x_axis_value(name=invalid_axis_name)

        # Then
        assert axis_value == ChartAxisFields.date.value

    @pytest.mark.parametrize(
        "valid_name",
        [
            "stratum",
            "date",
            "metric",
        ],
    )
    def test_get_y_axis_value_for_valid_name(self, valid_name: str):
        """
        Given a name of an axis type
        When `get_y_axis_value()` is called from the `ChartAxisFields` enum class
        Then the correct value is returned
        """
        # Given
        valid_axis_name = valid_name

        # When
        axis_value = ChartAxisFields.get_y_axis_value(name=valid_axis_name)

        # Then
        assert axis_value == ChartAxisFields[valid_axis_name].value

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "",
            "-",
            None,
        ],
    )
    def test_get_y_axis_value_for_invalid_name_returns_default(self, invalid_name: str):
        """
        Given an invalid name for an axis type
        When `get_y_axis_value()` is called from the `ChartAxisFields` enum class
        Then the value of the default of `metric` is returned
        """
        # Given
        invalid_axis_name = invalid_name

        # When
        axis_value = ChartAxisFields.get_y_axis_value(name=invalid_axis_name)

        # Then
        assert axis_value == ChartAxisFields.metric.value

    def test_values(self):
        """
        Given no input
        When the `values()` class method is called
            from the `ChartAxisFields` enum
        Then the correct tuple is returned
        """
        # Given / When
        values = ChartAxisFields.values()

        # Then
        expected_values = (
            "stratum__name",
            "age__name",
            "date",
            "metric_value",
            "geography__name",
            "sex",
        )
        assert values == expected_values


class TestChartTypes:
    def test_choices(self):
        """
        Given no input
        When the `choices()` class method is called
            from the `ChartTypes` enum
        Then the correct tuple is returned
        """
        # Given / When
        choices = ChartTypes.choices()

        # Then
        _choices = (
            "line_with_shaded_section",
            "bar",
            "line_multi_coloured",
            "line_single_simplified",
            "stacked_bar",
            "pyramid",
        )
        assert choices == tuple((choice, choice) for choice in _choices)

    @pytest.mark.parametrize(
        "expected_choice",
        (
            "line_with_shaded_section",
            "bar",
            "line_multi_coloured",
        ),
    )
    def test_selectable_choices(self, expected_choice: str):
        """
        Given an expected choice
        When the `selectable_choices()` class method is called
            from the `ChartTypes` enum
        Then choice is in the returned selectable choices
        """
        # Given / When
        choices = ChartTypes.selectable_choices()

        # Then
        assert (expected_choice, expected_choice) in choices

    def test_headline_selectable_choices(self):
        """
        Given an expected choice
        When the `selectable_headline_choices()` class method is called
            from the `ChartTypes` enum
        Then choice is in the returned selectable choices
        """
        # Given
        expected_choice = "bar"

        # When
        choices = ChartTypes.selectable_headline_choices()

        # Then
        assert (expected_choice, expected_choice) in choices

    def test_simplified_chart_selectable_choices(self):
        """
        Given an expected chioce
        When the `selectable_simplified_chart_choices()` class method is called
        Then choice is in the returned selectable choices
        """
        # Given
        expected_choice = "line_single_simplified"

        # When
        choices = ChartTypes.selectable_simplified_chart_choices()

        # Then
        assert (expected_choice, expected_choice) in choices

    def test_values(self):
        """
        Given no input
        When the `values()` class method is called
            from the `ChartTypes` enum
        Then the correct list is returned
        """
        # Given / When
        values = ChartTypes.values()

        # Then
        expected_values = [
            "line_with_shaded_section",
            "bar",
            "line_multi_coloured",
            "line_single_simplified",
            "stacked_bar",
            "pyramid",
        ]
        assert values == expected_values


class TestCheckForSubstringMatch:
    @pytest.mark.parametrize(
        "metric_name",
        [
            "COVID-19_cases_casesByDay",
            "COVID-19_cases_countRollingMean",
            "COVID-19_cases_rateRollingMean",
            "COVID-19_deaths_ONSByDay",
            "COVID-19_deaths_ONSByWeek",
            "COVID-19_deaths_ONSRollingMean",
            "COVID-19_headline_7DayAdmissions",
            "COVID-19_headline_7DayAdmissionsChange",
            "COVID-19_headline_7DayAdmissionsPercentChange",
            "COVID-19_headline_ONSdeaths_7DayChange",
            "COVID-19_headline_ONSdeaths_7DayPercentChange",
            "COVID-19_headline_ONSdeaths_7DayTotals",
            "COVID-19_headline_cases_7DayChange",
            "COVID-19_headline_cases_7DayPercentChange",
            "COVID-19_headline_cases_7DayTotals",
            "COVID-19_headline_positivity_latest",
            "COVID-19_healthcare_admissionByDay",
            "COVID-19_healthcare_admissionRollingMean",
            "COVID-19_healthcare_occupiedBedsByDay",
            "COVID-19_testing_positivity7DayRolling",
            "RSV_headline_admissionRateLatest",
            "RSV_headline_positivityLatest",
            "RSV_healthcare_admissionRateByWeek",
            "RSV_testing_positivityByWeek",
            "adenovirus_headline_positivityLatest",
            "hMPV_headline_positivityLatest",
            "hMPV_testing_positivityByWeek",
            "influenza_headline_ICUHDUadmissionRateChange",
            "influenza_headline_ICUHDUadmissionRateLatest",
            "influenza_headline_positivityLatest",
            "influenza_healthcare_ICUHDUadmissionRateByWeek",
            "parainfluenza_headline_positivityLatest",
            "parainfluenza_testing_positivityByWeek",
            "rhinovirus_headline_positivityLatest",
            "rhinovirus_testing_positivityByWeek",
        ],
    )
    def test_returns_true_for_cases_deaths_healthcare_substrings(
        self, metric_name: str
    ):
        """
        Given a metric name and a collection of substrings
            of which 1 substring is contained within the metric name
        When `_check_for_substring_match()` is called
        Then True is returned
        """
        # Given
        substrings: tuple[str, ...] = (
            "cases",
            "deaths",
            "healthcare",
            "admission",
            "positivity",
        )

        # When
        substrings_are_matching: bool = _check_for_substring_match(
            string_to_check=metric_name, substrings=substrings
        )

        # Then
        assert substrings_are_matching

    @pytest.mark.parametrize(
        "metric_name",
        [
            "COVID-19_vaccinations_autumn22_uptakeByDay",
            "COVID-19_vaccinations_spring23_dosesByDay",
            "COVID-19_vaccinations_autumn22_dosesByDay",
            "COVID-19_vaccinations_spring23_uptakeByDay",
            "COVID-19_headline_vaccines_spring23Uptake",
            "COVID-19_headline_tests_7DayPercentChange",
            "COVID-19_headline_tests_7DayChange",
            "COVID-19_headline_tests_7DayTotals",
            "COVID-19_testing_PCRcountByDay",
            "COVID-19_headline_vaccines_spring23Total",
        ],
    )
    def test_returns_true_for_vaccination_testing_substrings(self, metric_name: str):
        """
        Given a metric name and a collection of substrings
            of which 1 substring is contained within the metric name
        When `_check_for_substring_match()` is called
        Then True is returned
        """
        # Given
        substrings: tuple[str, ...] = (
            "vaccine",
            "vaccination",
            "vaccinated",
            "tests",
            "pcr",
        )

        # When
        substrings_are_matching: bool = _check_for_substring_match(
            string_to_check=metric_name, substrings=substrings
        )

        # Then
        assert substrings_are_matching


class TestDataSourceFileType:
    @pytest.mark.parametrize(
        "metric_group, expected_return_value",
        (
            [
                ("headline", True),
                ("cases", False),
                ("deaths", False),
                ("healthcare", False),
                ("testing", False),
                ("vaccinations", False),
            ]
        ),
    )
    def test_is_headline_returns_the_correct_response(
        self,
        metric_group: str,
        expected_return_value: bool,
    ):
        """
        Given a valid metric with either a `Headline` or `Timeseries`
            metric group
        When the `is_headline` property is called
        Then the expected response is returned
        """
        # Given
        expected_is_headline_value = expected_return_value

        # When
        is_headline_value = DataSourceFileType[metric_group].is_headline

        # Then
        assert is_headline_value == expected_is_headline_value

    @pytest.mark.parametrize(
        "metric_group, expected_return_value",
        (
            [
                ("headline", False),
                ("cases", True),
                ("deaths", True),
                ("testing", True),
                ("healthcare", True),
                ("vaccinations", True),
            ]
        ),
    )
    def test_is_timeseries_returns_the_correct_response(
        self,
        metric_group: str,
        expected_return_value: bool,
    ):
        """
        Given a valid metric with either a `Headline` or `Timeseries`
            metric group
        When the `is_timeseries` property is called
        Then the expected response is returned
        """
        # Given
        expected_is_timeseries_value = expected_return_value

        # When
        is_timeseries_value = DataSourceFileType[metric_group].is_timeseries

        # Then
        assert is_timeseries_value == expected_is_timeseries_value


class TestExtractMetricGroup:
    @pytest.mark.parametrize(
        "metric, metric_group",
        (
            [
                ("COVID-19_headline_vaccines_spring24Uptake", "headline"),
                ("COVID-19_headline_cases_7DayPercentChange", "headline"),
                ("COVID-19_cases_casesByDay", "cases"),
                ("RSV_testing_positivityByWeek", "testing"),
                ("COVID-19_deaths_ONSRegByWeek", "deaths"),
                ("COVID-19_healthcare_occupiedBedsRollingMean", "healthcare"),
                ("COVID-19_vaccinations_autumn23_uptakeByDay", "vaccinations"),
            ]
        ),
    )
    def test_extract_metric_returns_correct_metric_group(
        self, metric: str, metric_group: str
    ):
        """
        Given a valid metric string
        When the `extract_metric_group_from_metric()` is called
            with the metric value as its parameter
        Then the expected metric_group is returned
        """
        # Given
        expected_metric_group = metric_group

        # When
        returned_metric_group = extract_metric_group_from_metric(metric=metric)

        # Then
        assert returned_metric_group == expected_metric_group

    @pytest.mark.parametrize(
        "metric",
        (
            [
                "none-existent-metric-value",
                "COVID-19_invalid_metric",
            ]
        ),
    )
    def test_extract_metric_raises_error(self, metric: str):
        """
        Given an invalid metric
        When the `extract_metric_group_from_metric()` is called
            with the metric value as its parameter
        Then a `ValueError` is raised.
        """
        # Given
        invalid_metric = metric

        # When / Then
        with pytest.raises(ValueError):
            extract_metric_group_from_metric(metric=invalid_metric)
