import pytest
from pydantic_core._pydantic_core import ValidationError

from ingestion.data_transfer_models.time_series import (
    InboundTimeSeriesSpecificFields,
    TimeSeriesDTO,
)
from metrics.data.enums import TimePeriod


class TestTimeSeriesDTOForMetricFrequency:
    @pytest.mark.parametrize(
        "metric_frequency",
        (
            TimePeriod.Daily.name,
            TimePeriod.Weekly.name,
            TimePeriod.Fortnightly.name,
            TimePeriod.Monthly.name,
            TimePeriod.Quarterly.name,
            TimePeriod.Annual.name,
        ),
    )
    def test_valid_metric_frequency_values_are_deemed_valid(
        self,
        metric_frequency: str,
        valid_payload_for_base_model: dict[str, str],
        example_time_series_data,
    ):
        """
        Given a payload containing a valid `metric_frequency` value
        When the `TimeSeriesDTO` model is initialized
        Then model is deemed valid
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric_frequency"] = metric_frequency
        payload["time_series"] = [
            InboundTimeSeriesSpecificFields(**individual_source_data)
            for individual_source_data in example_time_series_data["time_series"]
        ]

        # When
        incoming_base_validation = TimeSeriesDTO(**payload)

        # Then
        incoming_base_validation.model_validate(
            incoming_base_validation,
            strict=True,
        )

    @pytest.mark.parametrize(
        "metric_frequency",
        ("D", "d", "day", "m", "M", "week", "W"),
    )
    def test_invalid_metric_frequency_value_throws_error(
        self, metric_frequency: str, valid_payload_for_base_model: dict[str, str]
    ):
        """
        Given a payload containing an invalid `metric_frequency`
        When the `TimeSeriesDTO` model is initialized
        Then a `ValidationError` is raised
        """
        # Given
        payload = valid_payload_for_base_model
        payload["metric_frequency"] = metric_frequency

        # When
        with pytest.raises(ValidationError):
            TimeSeriesDTO(**payload)
