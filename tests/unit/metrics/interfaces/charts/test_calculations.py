from typing import List

import pytest

from metrics.interfaces.charts import calculations


class TestSplitListInHalf:
    @pytest.mark.parametrize(
        "original_list, expected_first_half, expected_second_half",
        (
            ([1, 2], [1], [2]),
            ([1, 2, 3], [1], [2, 3]),
            ([1, 2, 3, 4], [1, 2], [3, 4]),
        ),
    )
    def test_split_list_in_half(
        self,
        original_list: List[int],
        expected_first_half: List[int],
        expected_second_half: List[int],
    ):
        """
        Given a list of integers
        When `split_list_in_half()` is called
        Then the list is split into 2 halves
        """
        # Given
        values = original_list

        # When
        first_half, second_half = calculations.split_list_in_half(values=values)

        # Then
        assert first_half == expected_first_half
        assert second_half == expected_second_half

    def test_split_list_in_half_for_fourteen_length_list(self):
        """
        Given a list of 14 numbers
        When `split_list_in_half()` is called
        Then the list is split into 2 halves
        """
        # Given
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

        # When
        first_half, second_half = calculations.split_list_in_half(values=values)

        # Then
        assert first_half == [1, 2, 3, 4, 5, 6, 7]
        assert second_half == [8, 9, 10, 11, 12, 13, 14]


class TestChangeBetweenEachHalf:
    @pytest.mark.parametrize(
        "values, expected_difference",
        (
            ([1, 2, 3, 5], 5),
            ([2, 3], 1),
            ([0.1, 0.3, 0.4, 0.5], 0.5),
            ([-1, 2, 3, -2, 1], 1),
        ),
    )
    def test_calculates_difference_correctly(
        self, values: List[int], expected_difference: int
    ):
        """
        Given a list of values
        When `change_over_each_half()` is called
        Then the correct calculated change in value between each half is returned
        """
        # Given
        values = values

        # When
        calculated_change = calculations.change_between_each_half(values=values)

        # Then
        assert calculated_change == expected_difference


class TestGetRollingPeriodSliceForEachHalf:
    def test_daily_metric_name(self):
        """
        Given a metric name which does not contain the word `weekly`
        When `get_rolling_period_slice_for_metric()` is called
        Then the rolling period slice of 7 is returned
        """
        # Given
        metric_name = "new_cases_daily"

        # When
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )

        # Then
        assert rolling_period_slice == 7

    def test_weekly_metric_name(self):
        """
        Given a metric name which does not contain the word `weekly`
        When `get_rolling_period_slice_for_metric()` is called
        Then the rolling period slice of 1 is returned
        """
        # Given
        metric_name = "weekly_positivity"

        # When
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )

        # Then
        assert rolling_period_slice == 1
