import pytest

from metrics.domain.utils import (
    ChartAxisFields,
    _check_for_substring_match,
    get_axis_name,
)


class TestGetAxisName:
    test_values = [(enums.value, enums.name) for enums in ChartAxisFields]
    test_values.append(("not_a_field", "not_a_field"))

    @pytest.mark.parametrize("field_name, expected_result", test_values)
    def test_get_axis_field_name(self, field_name: str, expected_result: str):
        """
        Given a field name (eg. stratum__name)
        When `get_axis_field_name()` is called
        Then the expected output will be returned
        """

        # Given
        input_field_name: str = field_name

        # When
        actual_result: str = get_axis_name(field_name=input_field_name)

        # Then
        assert actual_result == expected_result

    @pytest.mark.parametrize(
        "valid_name",
        [
            "stratum",
            "date",
            "metric",
            "geography",
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
            "geography",
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
            "COVID-19_headline_ONSdeaths_7daychange",
            "COVID-19_headline_ONSdeaths_7daypercentchange",
            "COVID-19_headline_ONSdeaths_7daytotals",
            "COVID-19_headline_cases_7DayChange",
            "COVID-19_headline_cases_7DayPercentChange",
            "COVID-19_headline_cases_7DayTotals",
            "COVID-19_headline_positivity_latest",
            "COVID-19_healthcare_AdmissionsByDay",
            "COVID-19_healthcare_AdmissionsRollingMean",
            "COVID-19_healthcare_OccupiedBedsByDay",
            "COVID-19_testing_7daypositivity",
            "RSV_headline_hospadmissionrateLatest",
            "RSV_headline_positivityLatest",
            "RSV_healthcare_hospadmissionrateByWeek",
            "RSV_testing_positivityByWeek",
            "adenovirus_headline_positivityLatest",
            "hMPV_headline_positivityLatest",
            "hMPV_testing_positivityByWeek",
            "influenza_headline_ICUHDUadmissionrateChange",
            "influenza_headline_ICUHDUadmissionrateLatest",
            "influenza_headline_positivityLatest",
            "influenza_healthcare_ICUHDUadmissionrateByWeek",
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
            "COVID-19_headline_totalvaccineuptake_spring23",
            "COVID-19_headline_tests_7DayPercentChange",
            "COVID-19_headline_tests_7DayChange",
            "COVID-19_headline_tests_7DayTotals",
            "COVID-19_testing_PCRcountByDay",
            "COVID-19_headline_totalvaccines_spring23",
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
