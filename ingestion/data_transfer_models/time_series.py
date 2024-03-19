import datetime

from pydantic import BaseModel, field_validator

from ingestion.data_transfer_models.base import IncomingBaseDataModel
from ingestion.metrics_interface.interface import MetricsAPIInterface
from ingestion.utils import type_hints


class InboundTimeSeriesSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for time series type data"""

    epiweek: int
    date: datetime.date
    embargo: datetime.datetime | None
    metric_value: float


class TimeSeriesDTO(IncomingBaseDataModel):
    metric_frequency: str
    time_series: list[InboundTimeSeriesSpecificFields]

    @field_validator("metric_frequency")
    @classmethod
    def cast_metric_frequency_to_an_expected_value(cls, *, metric_frequency: str):
        """Casts the `metric_frequency` value to one of the expected values

        Notes:
            Expected values are dictated by the `TimePeriod` enum

        Returns:
            A string representation of the parsed metric_frequency value

        """
        time_period_enum = MetricsAPIInterface.get_time_period_enum()
        return time_period_enum[metric_frequency.title()].value


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
