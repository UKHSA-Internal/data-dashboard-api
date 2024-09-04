import pytest
from unittest import mock
from decimal import Decimal

from metrics.domain.charts.line_single_simplified.utils import (
    return_formatted_max_y_axis_value,
)

MODULE_PATH = "metrics.domain.charts"


class TestReturnFormattedMaxYAxisValue:
    @mock.patch(
        f"{MODULE_PATH}.line_single_simplified.utils.convert_large_numbers_to_short_text"
    )
    def test_return_formatted_max_y_axis_value_delegates_calls_correctly(
        self,
        spy_convert_large_numbers_to_short_text: mock.MagicMock,
    ):
        """
        Given a valid `y_axis_values` list
        When `return_formatted_max_y_axis_value()` is called
        Then `_convert_large_numbers_to_short_text()` is called with an integer
        """
        # Given
        fake_y_axis_values = [Decimal(1.2), Decimal(2.9), Decimal(1.6)]
        expected_number = 3

        # When
        return_formatted_max_y_axis_value(y_axis_values=fake_y_axis_values)

        # Then
        spy_convert_large_numbers_to_short_text.assert_called_once_with(
            number=expected_number
        )

    @pytest.mark.parametrize(
        "y_axis_values, expected_return_value",
        (
            [
                ([Decimal(1.2), Decimal(1.3), Decimal(1.4)], "1"),
                ([Decimal(1.2), Decimal(1.3), Decimal(1.6)], "2"),
                ([Decimal(1.2), Decimal(2.2), Decimal(1.6)], "2"),
                ([Decimal(1.2), Decimal(2.9), Decimal(1.6)], "3"),
                ([Decimal(1.2), Decimal(9.9), Decimal(1.6)], "10"),
                ([Decimal(39.2), Decimal(75.9), Decimal(10.6)], "80"),
                ([Decimal(130.2), Decimal(103.3), Decimal(100.4)], "100"),
                ([Decimal(100.2), Decimal(220.3), Decimal(240.6)], "200"),
                ([Decimal(790.2), Decimal(840.2), Decimal(800.6)], "800"),
                ([Decimal(1300.2), Decimal(1003.3), Decimal(1000.4)], "1k"),
                ([Decimal(2000.2), Decimal(2500.0), Decimal(2400.6)], "2k"),
                ([Decimal(8000.2), Decimal(8550.2), Decimal(8300.6)], "9k"),
                ([Decimal(1300000.2), Decimal(1003000.3), Decimal(1000000.4)], "1m"),
                ([Decimal(2000000.2), Decimal(2500000.0), Decimal(2400000.6)], "2m"),
                ([Decimal(8000000.2), Decimal(8550000.2), Decimal(8300000.6)], "9m"),
            ]
        ),
    )
    def test_return_formatted_max_y_axis_value_returns_correct_value(
        self,
        y_axis_values: list[Decimal],
        expected_return_value: str,
    ):
        """
        Given a valid `y_axis_values` list of decimal values
        When `return_formatted_max_y_axis_value()` is called with `y_axis_values`
        Then a string of the maximum value formatted as a short value is returned.
        """
        # Given
        fake_y_axis_values = y_axis_values
        expected_max_value = expected_return_value

        # When
        max_value_return_value = return_formatted_max_y_axis_value(
            y_axis_values=fake_y_axis_values
        )

        # Then
        assert max_value_return_value == expected_max_value

    def test_return_formatted_max_y_value_raises_error_when_number_is_to_high(self):
        """
        Given an invalid `y_axis_value` list that contains a number of a billion or higher
        When the `return_formatted_max_y_axis_value()` method is called
        Then a `ValueError` is raised.
        """
        # Given
        fake_y_axis_values = [Decimal(3000.5), Decimal(1000000000.10)]

        with pytest.raises(ValueError):
            return_formatted_max_y_axis_value(y_axis_values=fake_y_axis_values)
