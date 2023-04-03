import datetime

import pytest

from metrics.data.access.core_models import (
    get_date_n_months_ago_from_timestamp,
    unzip_values,
)


class TestGetDateNMonthsAgoFromTimestamp:
    def test_for_timestamp_of_january(self):
        """
        Given a datetime stamp of January, and an arg to get the date 1 month ago
        When `get_date_n_months_ago_from_timestamp()` is called
        Then the 1st December of the previous year (1 month ago) is returned
        """
        # Given
        datetime_stamp = datetime.datetime(year=2023, month=1, day=15)
        number_of_months_ago = 1

        # When
        n_months_ago: datetime.datetime = get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime_stamp,
            number_of_months=number_of_months_ago,
        )

        # Then
        expected_month: int = 12
        expected_year: int = datetime_stamp.year - 1
        # The given timestamp is in Jan, so December of the previous should be returned
        assert n_months_ago.month == expected_month
        assert n_months_ago.day == 1
        assert n_months_ago.year == expected_year

    @pytest.mark.parametrize(
        "timestamp_month_number", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    )
    def test_for_timestamps_within_the_same_year(self, timestamp_month_number: int):
        """
        Given a datetime stamp of within a particular year, and an arg to get the date 1 month ago
        When `get_date_n_months_ago_from_timestamp()` is called
        Then the 1st of the previous month is returned
        """
        # Given
        datetime_stamp = datetime.datetime(
            year=2023, month=timestamp_month_number, day=15
        )
        number_of_months_ago = 1

        # When
        n_months_ago: datetime.datetime = get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime_stamp,
            number_of_months=number_of_months_ago,
        )

        # Then
        expected_month: int = datetime_stamp.month - 1
        assert n_months_ago.month == expected_month
        assert n_months_ago.day == 1
        assert n_months_ago.year == datetime_stamp.year


def test_unzip_values():
    """
    Given a list of 3 * 2-item tuples
    When `unzip_values()` is called
    Then the result is 2 tuples which contain 3 items each
    """
    # Given
    values = [(1, 2), (3, 4), (5, 6)]

    # When
    unzipped_lists = unzip_values(values)

    # Then
    first_index_item_unzipped_result, second_index_item_unzipped_result = unzipped_lists

    assert first_index_item_unzipped_result == (1, 3, 5)
    assert second_index_item_unzipped_result == (2, 4, 6)
