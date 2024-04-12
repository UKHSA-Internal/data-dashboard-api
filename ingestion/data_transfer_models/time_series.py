import datetime

from pydantic import BaseModel, field_validator
from pydantic.fields import Field
from pydantic_core.core_schema import ValidationInfo

from ingestion.data_transfer_models import validation
from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.utils import type_hints


class InboundTimeSeriesSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for time series type data"""

    epiweek: int = Field(ge=1, le=53)
    date: datetime.date
    embargo: datetime.datetime | None
    metric_value: float


class TimeSeriesDTO(IncomingBaseDataModel):
    metric_frequency: str
    time_series: list[InboundTimeSeriesSpecificFields]

    @field_validator("metric_frequency")
    @classmethod
    def cast_metric_frequency_to_an_expected_value(cls, metric_frequency: str):
        """Casts the `metric_frequency` value to one of the expected values

        Notes:
            Expected values are dictated by the `TimePeriod` enum

        Returns:
            A string representation of the parsed metric_frequency value

        Raises:
            `ValidationError`: If the `metric_frequency` does not
                conform to one of the expected values

        """
        return validation.validate_metric_frequency(metric_frequency=metric_frequency)

    @field_validator("time_series")
    @classmethod
    def validate_time_series(
        cls,
        time_series: list[InboundTimeSeriesSpecificFields],
        validation_info: ValidationInfo,
    ) -> list[InboundTimeSeriesSpecificFields]:
        """Validates the `time_series` value to check it conforms to expected rules

        Notes:
            If the `metric_frequency` is "D" (daily),
            then each `time_series` must 1 day apart.
            If the `metric_frequency` is "W" (weekly),
            then each `time_series` must be 7 days apart.
            If the above rules do not hold true where relevant,
            then the validation checks will fail.

        Args:
            time_series: List of enriched `InboundTimeSeriesSpecificFields`
                models containing `date` and metric values
                for the individual time series records
           validation_info: An enriched `ValidationInfo` instance
                provided by the pydantic model, this gives us
                the rest of the payload to the model initialization.
                From this, the `metric_frequency` is extracted,
                so it can be used in the downstream validation checks

        Returns:
            The list of enriched `InboundTimeSeriesSpecificFields`
            unchanged if all validation checks passed

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        input_metric_frequency: str | None = validation_info.data.get(
            "metric_frequency"
        )
        return validation.validate_time_series(
            time_series=time_series, metric_frequency=input_metric_frequency
        )


def _build_time_series_dto(
    *,
    source_data: type_hints.INCOMING_DATA_TYPE,
    enriched_specific_fields: list[InboundTimeSeriesSpecificFields],
) -> TimeSeriesDTO:
    return TimeSeriesDTO(
        parent_theme=source_data["parent_theme"],
        child_theme=source_data["child_theme"],
        topic=source_data["topic"],
        metric_group=source_data["metric_group"],
        metric=source_data["metric"],
        metric_frequency=source_data["metric_frequency"],
        geography_type=source_data["geography_type"],
        geography=source_data["geography"],
        geography_code=source_data["geography_code"],
        age=source_data["age"],
        sex=source_data["sex"],
        stratum=source_data["stratum"],
        refresh_date=source_data["refresh_date"],
        time_series=enriched_specific_fields,
    )


def _build_enriched_time_series_specific_fields(
    *,
    source_data: type_hints.INCOMING_DATA_TYPE,
) -> list[InboundTimeSeriesSpecificFields]:
    return [
        InboundTimeSeriesSpecificFields(
            epiweek=individual_time_series["epiweek"],
            date=individual_time_series["date"],
            embargo=individual_time_series["embargo"],
            metric_value=individual_time_series["metric_value"],
        )
        for individual_time_series in source_data["time_series"]
        if individual_time_series["metric_value"] is not None
    ]
