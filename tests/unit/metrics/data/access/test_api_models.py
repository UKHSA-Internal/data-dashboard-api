from typing import Dict, List, Union
from unittest import mock

from metrics.data.access.api_models import (
    filter_is_list,
    filter_is_string,
    validate_filter_name,
    validate_plot_filter,
    validate_query_filters,
)


class TestFilterIsList:
    def test_filter_is_list(self):
        """
        Given a field name (eg. geography)
        When `filter_is_list()` is called
        Then the expected output will be returned
        """
        # Given
        field_name = "geography"

        # When
        actual_result: str = filter_is_list(field_name=field_name)

        # Then
        expected_result = "geography__in"

        assert actual_result == expected_result


class TestFilterIsString:
    def test_filter_is_string_for_basic_behaviour(self):
        """
        Given a field name (eg. geography)
        When `filter_is_string()` is called
        Then the expected output will be returned
        """
        # Given
        field_name = "geography"

        # When
        actual_result: str = filter_is_string(field_name=field_name)

        # Then
        expected_result = field_name

        assert actual_result == expected_result

    def test_filter_is_string_handles_date_from(self):
        """
        Given a field name of date_from
        When `filter_is_string()` is called
        Then the expected output will be returned
        """
        # Given
        field_name = "date_from"

        # When
        actual_result: str = filter_is_string(field_name=field_name)

        # Then
        expected_result = "dt__gte"

        assert actual_result == expected_result


class TestValidateFilterName:
    @mock.patch("metrics.data.access.api_models.filter_is_list")
    def test_validate_filter_name_calls_list_function(self, mock_validate_filter_name):
        """
        Given a field name and filter value
        When `validate_filter_name()` is called and the filter value is a list of values
        Then `filter_is_list` is called
        """
        # Given
        field_name = "metric"
        filter_value = []

        # When
        actual_result: str = validate_filter_name(
            field_name=field_name, filter_value=filter_value
        )

        # Then
        mock_validate_filter_name.assert_called_once()
        assert actual_result == mock_validate_filter_name.return_value

    @mock.patch("metrics.data.access.api_models.filter_is_string")
    def test_validate_filter_name_calls_string_function(
        self, mock_validate_filter_name
    ):
        """
        Given a field name and filter value
        When `validate_filter_name()` is called and the filter value is a not a list of values
        Then `filter_is_string` is called
        """
        # Given
        field_name = "topic"
        filter_value = "COVID-19"

        # When
        actual_result: str = validate_filter_name(
            field_name=field_name, filter_value=filter_value
        )

        # Then
        mock_validate_filter_name.assert_called_once()
        assert actual_result == mock_validate_filter_name.return_value


class TestValidatePlotFilter:
    def test_validate_plot_filter_for_basic_behaviour(self):
        """
        Given a list of possible fields and a plot
        When `validate_plot_filter()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plot = {
            "topic": "COVID-19",
            "metric": "new_cases_daily",
        }

        # When
        actual_result: Dict[str, str] = validate_plot_filter(
            possible_fields=possible_fields,
            plot=plot,
        )

        # Then
        expected_result: Dict[str, str] = {
            "topic": "COVID-19",
            "metric": "new_cases_daily",
        }

        assert actual_result == expected_result

    def test_validate_plot_filter_date_from_is_handled_corretly(self):
        """
        Given a list of possible fields and a plot which includes a date_from field
        When `validate_plot_filter()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "date_from",
        ]
        plot = {
            "topic": "COVID-19",
            "date_from": "2023-02-25",
        }

        # When
        actual_result: Dict[str, str] = validate_plot_filter(
            possible_fields=possible_fields,
            plot=plot,
        )

        # Then
        expected_result: Dict[str, str] = {
            "topic": "COVID-19",
            "dt__gte": "2023-02-25",
        }

        assert actual_result == expected_result

    def test_validate_plot_filter_filter_is_a_list(self):
        """
        Given a list of possible fields and a plot which includes a list of filter values
        When `validate_plot_filter()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plot = {
            "topic": "COVID-19",
            "metric": ["new_cases_7day_avg", "new_cases_7day_avg"],
        }

        # When
        actual_result: Dict[str, str] = validate_plot_filter(
            possible_fields=possible_fields,
            plot=plot,
        )

        # Then
        expected_result: Dict[str, Union[str, List[str]]] = {
            "topic": "COVID-19",
            "metric__in": ["new_cases_7day_avg", "new_cases_7day_avg"],
        }

        assert actual_result == expected_result

    def test_validate_plot_filter_unknown_fields_are_ignored(self):
        """
        Given a list of possible fields and a plot which includes irrelevant content
        When `validate_plot_filter()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plot = {
            "topic": "COVID-19",
            "chart_type": "simple_line",
        }

        # When
        actual_result: Dict[str, str] = validate_plot_filter(
            possible_fields=possible_fields,
            plot=plot,
        )

        # Then
        expected_result = {
            "topic": "COVID-19",
        }

        assert actual_result == expected_result


class TestValidateQueryFilters:
    def test_validate_query_filters_for_basic_behaviour(self):
        """
        Given a list of possible fields and a single plot
        When `validate_query_filters()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plots = [
            {
                "topic": "COVID-19",
                "metric": "new_cases_daily",
            }
        ]

        # When
        actual_result: List[Dict[str, str]] = validate_query_filters(
            possible_fields=possible_fields,
            plots=plots,
        )

        # Then
        expected_result: List[Dict[str, str]] = [
            {
                "topic": "COVID-19",
                "metric": "new_cases_daily",
            }
        ]

        assert actual_result == expected_result

    def test_validate_query_filters_multiple_plots(self):
        """
        Given a list of possible fields and a list of plots
        When `validate_query_filters()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plots = [
            {"topic": "COVID-19", "metric": "new_cases_daily"},
            {"topic": "COVID-19", "metric": "new_cases_7day_avg"},
        ]

        # When
        actual_result: List[Dict[str, str]] = validate_query_filters(
            possible_fields=possible_fields,
            plots=plots,
        )

        # Then
        expected_result: List[Dict[str, str]] = [
            {"topic": "COVID-19", "metric": "new_cases_daily"},
            {"topic": "COVID-19", "metric": "new_cases_7day_avg"},
        ]

        assert actual_result == expected_result

    def test_validate_query_filters_date_from_is_handled_corretly(self):
        """
        Given a list of possible fields and a list of plots which includes a date_from
        When `validate_query_filters()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "date_from",
        ]
        plots = [
            {
                "topic": "COVID-19",
                "date_from": "2023-02-25",
            }
        ]

        # When
        actual_result: List[Dict[str, str]] = validate_query_filters(
            possible_fields=possible_fields,
            plots=plots,
        )

        # Then
        expected_result: List[Dict[str, str]] = [
            {
                "topic": "COVID-19",
                "dt__gte": "2023-02-25",
            }
        ]

        assert actual_result == expected_result

    def test_validate_query_filters_filter_is_a_list(self):
        """
        Given a list of possible fields and a list of plots which includes a list of filter values
        When `validate_query_filters()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plots = [
            {
                "topic": "COVID-19",
                "metric": ["new_cases_7day_avg", "new_cases_7day_avg"],
            }
        ]

        # When
        actual_result: List[Dict[str, str]] = validate_query_filters(
            possible_fields=possible_fields, plots=plots
        )

        # Then
        expected_result = [
            {
                "topic": "COVID-19",
                "metric__in": ["new_cases_7day_avg", "new_cases_7day_avg"],
            },
        ]

        assert actual_result == expected_result

    def test_validate_query_filters_unknown_fields_are_ignored(self):
        """
        Given a list of possible fields and a list of plots which includes irrelevant content
        When `validate_query_filters()` is called
        Then the expected output will be returned
        """
        # Given
        possible_fields = [
            "topic",
            "metric",
        ]
        plots = [
            {
                "topic": "COVID-19",
                "chart_type": "simple_line",
            }
        ]

        # When
        actual_result: List[Dict[str, str]] = validate_query_filters(
            possible_fields=possible_fields,
            plots=plots,
        )

        # Then
        expected_result = [
            {
                "topic": "COVID-19",
            },
        ]

        assert actual_result == expected_result
