import datetime

from pydantic import BaseModel

from ingestion.utils import type_hints
from ingestion.validation.base import IncomingBaseDataModel


class InboundHeadlineSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for headline type data"""

    period_start: datetime.date
    period_end: datetime.date
    embargo: datetime.datetime | None
    metric_value: float


class HeadlineDTO(IncomingBaseDataModel):
    data: list[InboundHeadlineSpecificFields]


def _build_headline_dto(
    source_data: type_hints.INCOMING_DATA_TYPE,
    enriched_specific_fields: list[InboundHeadlineSpecificFields],
) -> HeadlineDTO:
    return HeadlineDTO(
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
        data=enriched_specific_fields,
    )


def _build_enriched_headline_specific_fields(
    source_data: type_hints.INCOMING_DATA_TYPE,
) -> list[InboundHeadlineSpecificFields]:
    return [
        InboundHeadlineSpecificFields(
            period_start=individual_time_series["period_start"],
            period_end=individual_time_series["period_end"],
            embargo=individual_time_series["embargo"],
            metric_value=individual_time_series["metric_value"],
        )
        for individual_time_series in source_data["data"]
        if individual_time_series["metric_value"] is not None
    ]
