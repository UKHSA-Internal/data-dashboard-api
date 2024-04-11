import datetime

from pydantic import BaseModel, field_validator

from ingestion.data_transfer_models import validation
from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.utils import type_hints


class InboundTimeSeriesSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for time series type data"""

    epiweek: int
    date: datetime.date
    embargo: datetime.datetime | None
    metric_value: float

    @field_validator("embargo")
    @classmethod
    def cast_embargo_to_uk_timezone(
        cls, embargo: datetime.datetime
    ) -> datetime.datetime:
        """Casts the inbound `embargo` to the London timezone

        Args:
            embargo: The inbound embargo date
                datetime object

        Returns:
            A `datetime` object which has the timezone
            info set to the declared `TIMEZONE` as per
            the main django settings

        """
        return validation.cast_date_to_uk_timezone(date_value=embargo)


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
