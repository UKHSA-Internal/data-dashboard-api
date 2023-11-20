import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.validation.time_series import IncomingTimeSeriesValidation

VALID_DATETIME = "2023-11-20 12:00:00"


class TestIncomingTimeSeriesValidation:
    def test_validates_payload(self):
        """
        Given a payload containing valid values
        When the `IncomingTimeSeriesValidation` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_epiweek = 46
        fake_date = "2023-11-01"
        fake_embargo = VALID_DATETIME
        fake_metric_value = 123

        # When
        incoming_headline_validation = IncomingTimeSeriesValidation(
            epiweek=fake_epiweek,
            date=fake_date,
            embargo=fake_embargo,
            metric_value=fake_metric_value,
        )

        # Then
        incoming_headline_validation.model_validate(
            incoming_headline_validation,
            strict=True,
        )

    def test_raises_error_when_datetime_passed_to_epiweek(self):
        """
        Given a payload containing a datetime string for `epiweek`
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_epiweek = VALID_DATETIME
        fake_date = "2023-11-27"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingTimeSeriesValidation(
                epiweek=fake_epiweek,
                date=fake_date,
                embargo=VALID_DATETIME,
                metric_value=123,
            )

    def test_raises_error_when_datetime_passed_to_period_end(self):
        """
        Given a payload containing a datetime string for `date`
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_date = VALID_DATETIME
        fake_epiweek = 46
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingTimeSeriesValidation(
                date=fake_date,
                epiweek=fake_epiweek,
                embargo=fake_embargo,
                metric_value=123,
            )

    def test_raises_error_when_date_passed_to_embargo(self):
        """
        Given a payload containing a date string for `embargo`
        When the `IncomingTimeSeriesValidation` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_date = "2023-11-20"
        fake_epiweek = 46
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            IncomingTimeSeriesValidation(
                date=fake_date,
                epiweek=fake_epiweek,
                embargo=fake_embargo,
                metric_value=123,
            )
