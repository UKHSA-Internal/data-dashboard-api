import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from ingestion.validation.time_series import (
    InboundTimeSeriesSpecificFields,
    TimeSeriesDTO,
)

VALID_DATETIME = "2023-11-20 12:00:00"


class TestInboundTimeSeriesSpecificFields:
    def test_validates_payload(self):
        """
        Given a payload containing valid values
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then model is deemed valid
        """
        # Given
        fake_epiweek = 46
        fake_date = "2023-11-01"
        fake_embargo = VALID_DATETIME
        fake_metric_value = 123

        # When
        imbound_time_series_specific_fields_validation = (
            InboundTimeSeriesSpecificFields(
                epiweek=fake_epiweek,
                date=fake_date,
                embargo=fake_embargo,
                metric_value=fake_metric_value,
            )
        )

        # Then
        imbound_time_series_specific_fields_validation.model_validate(
            imbound_time_series_specific_fields_validation,
            strict=True,
        )

    def test_raises_error_when_datetime_passed_to_epiweek(self):
        """
        Given a payload containing a datetime string for `epiweek`
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_epiweek = VALID_DATETIME
        fake_date = "2023-11-27"

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(
                epiweek=fake_epiweek,
                date=fake_date,
                embargo=VALID_DATETIME,
                metric_value=123,
            )

    def test_raises_error_when_datetime_passed_to_period_end(self):
        """
        Given a payload containing a datetime string for `date`
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_date = VALID_DATETIME
        fake_epiweek = 46
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(
                date=fake_date,
                epiweek=fake_epiweek,
                embargo=fake_embargo,
                metric_value=123,
            )

    def test_raises_error_when_date_passed_to_embargo(self):
        """
        Given a payload containing a date string for `embargo`
        When the `InboundTimeSeriesSpecificFields` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        fake_date = "2023-11-20"
        fake_epiweek = 46
        fake_embargo = "2023-11-30"

        # When / Then
        with pytest.raises(ValidationError):
            InboundTimeSeriesSpecificFields(
                date=fake_date,
                epiweek=fake_epiweek,
                embargo=fake_embargo,
                metric_value=123,
            )


class TestTimeSeriesDTO:
    def test_casts_upper_and_lower_level_fields(
        self, example_time_series_data_v2: INCOMING_DATA_TYPE
    ):
        """
        Given valid incoming source data for a headline data type
        When the `TimeSeriesDTO` is initialized with a list of
            initialized `InboundTimeSeriesSpecificFields` models
        Then the payload is deemed valid
        """
        # Given
        source_data = example_time_series_data_v2

        # When
        lower_level_fields = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in source_data["time_series"]
        ]

        time_series_dto = TimeSeriesDTO(
            parent_theme=source_data["parent_theme"],
            child_theme=source_data["child_theme"],
            topic=source_data["topic"],
            metric_group=source_data["metric_group"],
            metric=source_data["metric"],
            geography_type=source_data["geography_type"],
            geography=source_data["geography"],
            geography_code=source_data["geography_code"],
            age=source_data["age"],
            sex=source_data["sex"],
            stratum=source_data["stratum"],
            refresh_date=source_data["refresh_date"],
            time_series=lower_level_fields,
        )

        # Then
        time_series_dto.model_validate(time_series_dto)
