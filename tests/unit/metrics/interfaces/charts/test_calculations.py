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
        original_list: list[int],
        expected_first_half: list[int],
        expected_second_half: list[int],
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
        self, values: list[int], expected_difference: int
    ):
        """
        Given a list of values
        When `change_over_each_half()` is called
        Then the correct calculated change in value between each half is returned
        """
        # Given
        values_to_calculate = values

        # When
        calculated_change = calculations.change_between_each_half(
            values=values_to_calculate
        )

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
        metric_name = "COVID-19_deaths_ONSByDay"

        # When
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )

        # Then
        assert rolling_period_slice == 7

    @pytest.mark.parametrize(
        "metric_name",
        [
            "influenza_healthcare_ICUHDUadmissionRateByWeek",
            "COVID-19_deaths_ONSByWeek",
            "RSV_healthcare_admissionRateByWeek",
            "RSV_testing_positivityByWeek",
            "adenovirus_testing_positivityByWeek",
            "hMPV_testing_positivityByWeek",
            "influenza_testing_positivityByWeek",
            "influenza_healthcare_ICUHDUadmissionRateByWeek",
            "parainfluenza_testing_positivityByWeek",
            "rhinovirus_testing_positivityByWeek",
        ],
    )
    def test_weekly_metric_name(self, metric_name: str):
        """
        Given a metric name for weekly-centric data
        When `get_rolling_period_slice_for_metric()` is called
        Then the rolling period slice of 1 is returned
        """
        # Given
        metric_name_for_weekly_data = metric_name

        # When
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name_for_weekly_data
        )

        # Then
        assert rolling_period_slice == 1
