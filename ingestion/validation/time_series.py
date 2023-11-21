import datetime

from pydantic import BaseModel

from ingestion.utils import type_hints
from ingestion.validation.base import IncomingBaseDataModel


class InboundTimeSeriesSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for time series type data"""

    epiweek: int
    date: datetime.date
    embargo: datetime.datetime
    metric_value: float


class TimeSeriesDTO(IncomingBaseDataModel):
    time_series: list[InboundTimeSeriesSpecificFields]


def _build_time_series_dto(
    source_data: type_hints.INCOMING_DATA_TYPE,
    enriched_specific_fields: list[InboundTimeSeriesSpecificFields],
) -> TimeSeriesDTO:
    return TimeSeriesDTO(
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
        time_series=enriched_specific_fields,
    )


def _build_enriched_time_series_specific_fields(
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
    ]
