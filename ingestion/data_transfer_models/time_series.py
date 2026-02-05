import datetime
from typing import Self

from pydantic import BaseModel, field_validator, model_validator
from pydantic.fields import Field

import validation
from ingestion.utils import type_hints
from metrics.api.settings.auth import ALLOW_MISSING_IS_PUBLIC_FIELD, AUTH_ENABLED
from validation.data_transfer_models.base import (
    IncomingBaseDataModel,
    NonPublicDataSentToPublicIngestionError,
)


class InboundTimeSeriesSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for time series type data"""

    epiweek: int = Field(ge=1, le=53)
    date: datetime.date
    embargo: datetime.datetime | None
    metric_value: float
    in_reporting_delay_period: bool = False
    force_write: bool = False
    is_public: bool

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

    @model_validator(mode="after")
    def invalidate_non_public_data_for_public_ingestion(self) -> Self:
        """Checks that if this is a public instance of the product then `is_public=False` data is invalidated."""
        if not AUTH_ENABLED and not self.is_public:
            raise NonPublicDataSentToPublicIngestionError

        return self


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
    def validate_in_reporting_delay_period_has_trailing_section_only(
        cls, time_series: list[InboundTimeSeriesSpecificFields]
    ) -> list[InboundTimeSeriesSpecificFields]:
        """Validates the `in_reporting_delay_period` values only contain a trailing section."""
        in_reporting_delay_period_values: list[bool] = [
            model.in_reporting_delay_period for model in time_series
        ]

        validation.validate_in_reporting_delay_period(
            in_reporting_delay_period_values=in_reporting_delay_period_values
        )

        return time_series


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
            in_reporting_delay_period=individual_time_series.get(
                "in_reporting_delay_period", False
            ),
            force_write=individual_time_series.get("force_write", False),
            is_public=individual_time_series["is_public"],
        )
        for individual_time_series in source_data["time_series"]
        if individual_time_series["metric_value"] is not None
    ]
