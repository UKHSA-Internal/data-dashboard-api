import datetime

import pytest

from ingestion.utils.dates import calculate_days_between_dates


class TestCalculateDaysBetweenDates:
    @pytest.mark.parametrize(
        "dates, expected_days_between",
        [
            (["2023-01-01", "2023-01-02"], {1}),
            (["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"], {1}),
            (["2023-01-01", "2023-01-04"], {3}),
            (["2023-01-01", "2023-01-04", "2023-01-05"], {3, 1}),
            (["2023-01-01", "2023-02-03", "2023-02-04"], {33, 1}),
        ],
    )
    def test_calculates_correct_unique_gaps(self, dates, expected_days_between):
        """
        Given a list of dates
        When `calculate_days_between_dates()` is called
        Then a set is returned containing
            the number of possible differences in days
            between the given list of dates
        """
        # Given
        input_dates = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in dates]

        # When
        calculated_days_between = calculate_days_between_dates(dates=input_dates)

        # Then
        assert calculated_days_between == expected_days_between
