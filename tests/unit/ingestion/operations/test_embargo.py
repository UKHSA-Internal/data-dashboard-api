import datetime
from unittest import mock

import pytest

from ingestion.operations.embargo import get_default_embargo

MODULE_PATH = "ingestion.operations.embargo"


class TestGetDefaultEmbargo:
    @pytest.mark.parametrize(
        "frozen_time",
        [
            "2023-10-27 01:00:01",  # Friday
            "2023-10-27 22:00:22",  # Friday
            "2023-10-28 23:00:00",  # Saturday
            "2023-10-29 11:00:00",  # Sunday
            "2023-10-30 10:00:13",  # Monday
            "2023-10-31 13:00:00",  # Tuesday
            "2023-11-01 12:00:28",  # Wednesday
            "2023-11-01 16:30:18",  # Wednesday
            "2023-11-02 16:30:00",  # Thursday (prior to cutoff)
            "2023-11-02 17:29:59",  # Thursday (prior to cutoff)
        ],
    )
    @mock.patch(f"{MODULE_PATH}._get_current_datetime")
    def test_returns_next_available_thursday_cutoff(
        self, mocked_get_current_date: mock.MagicMock, frozen_time: str
    ):
        """
        Given a current date and time which is frozen
            to be before the next available Thursday cutoff
            i.e. Friday 27th Oct 2023 up to Thursday 2nd Nov 2023
        When `get_default_embargo()` is called
        Then a datetime of Thurs 2nd Nov 2023 5.30pm is returned
        """
        # Given
        mocked_get_current_date.return_value = datetime.datetime.fromisoformat(
            frozen_time
        )

        # When
        default_embargo: datetime.datetime = get_default_embargo()

        # Then
        assert default_embargo.year == 2023
        assert default_embargo.month == 11
        # Check the `default_embargo` is set for the next
        # available Thursday at 5.30pm which in this case is the next day
        assert default_embargo.day == 2
        # Check that the associated cutoff time is set to be 5.30pm
        assert default_embargo.hour == 17
        assert default_embargo.minute == 30
        assert default_embargo.second == 0

    @pytest.mark.parametrize(
        "frozen_time",
        [
            "2023-11-02 17:45:00",  # Thursday (after cutoff)
            "2023-11-02 18:00:59",  # Thursday (after cutoff)
            "2023-11-02 20:00:05",  # Thursday (after cutoff)
            "2023-11-02 22:30:59",  # Thursday (after cutoff)
            "2023-11-02 23:59:59",  # Thursday (after cutoff)
        ],
    )
    @mock.patch(f"{MODULE_PATH}._get_current_datetime")
    def test_current_datetime_of_thursday_evening_sets_embargo_for_the_following_week(
        self, mocked_get_current_date: mock.MagicMock, frozen_time: str
    ):
        """
        Given a current date and time of Thursday evening
            which is later the cutoff time of 5.30pm
        When `get_default_embargo()` is called
        Then a datetime is returned for the following Thursday 5.30pm cutoff
            i.e. 1 week later than the current date
        """
        # Given
        mocked_get_current_date.return_value = datetime.datetime.fromisoformat(
            frozen_time
        )

        # When
        default_embargo: datetime.datetime = get_default_embargo()

        # Then
        assert default_embargo.year == 2023
        assert default_embargo.month == 11
        # Check the `default_embargo` is set for the next Thursday
        # because the cutoff time for the current day which is a Thursday has passed
        assert default_embargo.day == 9
        # Check that the associated cutoff time is set to be 5.30pm
        assert default_embargo.hour == 17
        assert default_embargo.minute == 30
        assert default_embargo.second == 0
