import datetime
from unittest import mock

import pytest

from metrics.domain.trends.state import TREND_AS_DICT, ArrowDirection, Colour, Trend

MODULE_PATH: str = "metrics.domain.trends.state"


class TestTrend:
    @staticmethod
    def _create_valid_payload() -> TREND_AS_DICT:
        period_end = datetime.date(year=2024, month=2, day=29)
        return {
            "metric_name": "COVID-19_headline_ONSdeaths_7DayChange",
            "metric_value": 24568,
            "metric_period_end": str(period_end),
            "percentage_metric_name": "COVID-19_headline_ONSdeaths_7DayPercentChange",
            "percentage_metric_value": -0.1,
            "percentage_metric_period_end": str(period_end),
        }

    def test_to_dict_returns_correct_data(self):
        """
        Given a valid payload used to create a `Trend` model
        When `dict()` is called from the instance of the `Trend` model
        Then returned dict contains the correct data
        """
        # Given
        valid_payload = self._create_valid_payload()
        trend = Trend(**valid_payload)

        # When
        trend_data: TREND_AS_DICT = trend.model_dump()

        # Then
        expected_trend_data = valid_payload
        expected_trend_data["direction"] = ArrowDirection.down.name
        expected_trend_data["colour"] = Colour.green.name
        assert trend_data == expected_trend_data

    @pytest.mark.parametrize(
        "metric_value, expected_direction",
        [
            (100, ArrowDirection.up.name),
            (0, ArrowDirection.neutral.name),
            (-100, ArrowDirection.down.name),
        ],
    )
    def test_direction_returns_correct_value(
        self, metric_value: int, expected_direction: str
    ):
        """
        Given a `Trend` model with a particular `metric_value`
        When `direction` is called from the instance of the `Trend` model
        Then the expected direction is returned depending on the `metric_value`
        """
        # Given
        valid_payload = self._create_valid_payload()
        valid_payload["percentage_metric_value"] = metric_value
        trend = Trend(**valid_payload)

        # When
        direction: str = trend.direction

        # Then
        assert direction == expected_direction

    def test_no_change_returns_neutral_colour(self):
        """
        Given a `Trend` model with a `metric_value` of 0
        When `colour` is called from the instance of the `Trend` model
        Then the "neutral" is returned to indicate no change in the `metric_value`
        """
        # Given
        valid_payload = self._create_valid_payload()
        valid_payload["percentage_metric_value"] = 0
        trend = Trend(**valid_payload)

        # When
        colour: str = trend.colour

        # Then
        assert colour == Colour.neutral.name

    @mock.patch(f"{MODULE_PATH}.is_metric_improving", return_value=True)
    def test_change_delegates_call_for_positive_change(
        self, spy_is_metric_improving: mock.MagicMock
    ):
        """
        Given a `Trend` model
        When `colour` is called from the instance of the `Trend` model
        Then the call is delegated to `is_metric_improving()`
        And "green" is returned to indicate a positive change
        """
        # Given
        valid_payload = self._create_valid_payload()
        trend = Trend(**valid_payload)

        # When
        colour: str = trend.colour

        # Then
        spy_is_metric_improving.assert_called_once_with(
            change_in_metric_value=trend.percentage_metric_value,
            metric_name=trend.metric_name,
        )
        assert colour == Colour.green.name

    @mock.patch(f"{MODULE_PATH}.is_metric_improving", return_value=False)
    def test_change_delegates_call_for_negative_change(
        self, spy_is_metric_improving: mock.MagicMock
    ):
        """
        Given a `Trend` model
        When `colour` is called from the instance of the `Trend` model
        Then the call is delegated to `is_metric_improving()`
        And "red" is returned to indicate a positive change
        """
        # Given
        valid_payload = self._create_valid_payload()
        trend = Trend(**valid_payload)

        # When
        colour: str = trend.colour

        # Then
        spy_is_metric_improving.assert_called_once_with(
            change_in_metric_value=trend.percentage_metric_value,
            metric_name=trend.metric_name,
        )
        assert colour == Colour.red.name
