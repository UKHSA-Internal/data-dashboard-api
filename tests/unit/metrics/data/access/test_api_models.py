from typing import Dict, List, Union

# import datetime

# import pytest

from metrics.data.access.api_models import create_filters


class TestCreateFilters:
    def test_for_basic_behaviour(self):
        """
        Given a list of possible fields and a plot
        When `create_filters()` is called
        Then the expected output will be returned
        """
        # Given
        filterset_fields = [
            "topic",
            "metric",
        ]
        plots = [{"topic": "COVID-19", "metric": "new_cases_daily"}]

        # When
        filter_result: List[Dict[str, str]] = create_filters(
            filterset_fields=filterset_fields,
            plots=plots,
        )

        # Then
        expected_result: List[Dict[str, str]] = [
            {
                "topic": "COVID-19",
                "metric": "new_cases_daily",
            }
        ]

        assert filter_result == expected_result

    def test_multiple_plots(self):
        """
        Given a list of possible fields and a list of plots
        When `create_filters()` is called
        Then the expected output will be returned
        """
        # Given
        filterset_fields = [
            "topic",
            "metric",
        ]
        plots = [
            {"topic": "COVID-19", "metric": "new_cases_daily"},
            {"topic": "COVID-19", "metric": "new_cases_7day_avg"},
        ]

        # When
        filter_result: List[Dict[str, str]] = create_filters(
            filterset_fields=filterset_fields,
            plots=plots,
        )

        # Then
        expected_result: List[Dict[str, str]] = [
            {"topic": "COVID-19", "metric": "new_cases_daily"},
            {"topic": "COVID-19", "metric": "new_cases_7day_avg"},
        ]

        assert filter_result == expected_result

    def test_date_from_is_handled_corretly(self):
        """
        Given a list of possible fields and a list of plots which includes a date_from
        When `create_filters()` is called
        Then the expected output will be returned
        """
        # Given
        filterset_fields = [
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
        filter_result: List[Dict[str, str]] = create_filters(
            filterset_fields=filterset_fields,
            plots=plots,
        )

        # Then
        expected_result: List[Dict[str, str]] = [
            {"topic": "COVID-19", "dt__gte": "2023-02-25"}
        ]

        assert filter_result == expected_result

    def test_filter_is_a_list(self):
        """
        Given a list of possible fields and a list of plots which includes a list of filter values
        When `create_filters()` is called
        Then the expected output will be returned
        """
        # Given
        filterset_fields = [
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
        filter_result: List[Dict[str, str]] = create_filters(
            filterset_fields=filterset_fields, plots=plots
        )

        # Then
        expected_result = [
            {
                "topic": "COVID-19",
                "metric__in": ["new_cases_7day_avg", "new_cases_7day_avg"],
            },
        ]

        assert filter_result == expected_result

    def test_unknown_fields_are_ignored(self):
        """
        Given a list of possible fields and a list of plots which includes irrelevant content
        When `create_filters()` is called
        Then the expected output will be returned
        """
        # Given
        filterset_fields = [
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
        filter_result: List[Dict[str, str]] = create_filters(
            filterset_fields=filterset_fields,
            plots=plots,
        )

        # Then
        expected_result = [
            {
                "topic": "COVID-19",
            },
        ]

        assert filter_result == expected_result
