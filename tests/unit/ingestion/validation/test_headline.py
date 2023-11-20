import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.validation.headline import IncomingHeadlineValidation

VALID_DATETIME = "2023-11-20 12:00:00"


class TestIncomingHeadlineValidation:
    def test_casts_dates_for_period_start_and_end(self):
        """
        Given a payload containing a date strings
            for `period_start` & `period_end`
        When the `IncomingHeadlineValidation` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = "2023-11-27"

        # When
        incoming_headline_validation = IncomingHeadlineValidation(
            period_start=fake_period_start,
            period_end=fake_period_end,
            embargo=VALID_DATETIME,
            metric_value=123,
        )

        # Then
        incoming_headline_validation.model_validate(
            incoming_headline_validation,
            strict=True,
        )

    def test_raises_error_when_datetime_passed_to_period_start(self):
        """
        Given a payload containing a datetime string for `period_start`
        When the `IncomingHeadlineValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_period_start = VALID_DATETIME
        fake_period_end = "2023-11-27"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingHeadlineValidation(
                period_start=fake_period_start,
                period_end=fake_period_end,
                embargo=VALID_DATETIME,
                metric_value=123,
            )

    def test_raises_error_when_datetime_passed_to_period_end(self):
        """
        Given a payload containing a datetime string for `period_end`
        When the `IncomingHeadlineValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = VALID_DATETIME

        # When / Then
        with pytest.raises(ValidationError):
            IncomingHeadlineValidation(
                period_start=fake_period_start,
                period_end=fake_period_end,
                embargo=VALID_DATETIME,
                metric_value=123,
            )

    def test_raises_error_when_date_passed_to_embargo(self):
        """
        Given a payload containing a date string for `embargo`
        When the `IncomingHeadlineValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_period_start = "2023-11-20"
        fake_period_end = "2023-11-27"
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingHeadlineValidation(
                period_start=fake_period_start,
                period_end=fake_period_end,
                embargo=fake_embargo,
                metric_value=123,
            )
