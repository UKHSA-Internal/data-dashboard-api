import pytest

from validation import validate_in_reporting_delay_period


class TestValidateInReportingDelayPeriod:

    @pytest.mark.parametrize(
        "invalid_in_reporting_delay_period_values",
        (
            [True, False, False, True],
            [True, False, False, False],
            [False, True, True, False],
        ),
    )
    def test_raises_error_for_invalid_sequences(
        self, invalid_in_reporting_delay_period_values: list[bool]
    ):
        """
        Given an invalid list of booleans
            which represent the in reporting delay periods
        When `validate_in_reporting_delay_period()` is called
        Then a `ValueError` is raised
        """
        # Given
        reporting_delay_period_values = invalid_in_reporting_delay_period_values

        # When / Then
        with pytest.raises(ValueError):
            validate_in_reporting_delay_period(
                in_reporting_delay_period_values=reporting_delay_period_values
            )

    @pytest.mark.parametrize(
        "valid_in_reporting_delay_period_values",
        (
            [False, False, False, True],
            [False, False, False, False],
            [False, False, True, True],
            [False, True, True, True],
        ),
    )
    def test_passes_for_valid_sequences(
        self, valid_in_reporting_delay_period_values: list[bool]
    ):
        """
        Given a valid list of booleans
            which represent the in reporting delay periods
        When `validate_in_reporting_delay_period()` is called
        Then no error is raised
        """
        # Given
        reporting_delay_period_values = valid_in_reporting_delay_period_values

        # When / Then
        validate_in_reporting_delay_period(
            in_reporting_delay_period_values=reporting_delay_period_values
        )
