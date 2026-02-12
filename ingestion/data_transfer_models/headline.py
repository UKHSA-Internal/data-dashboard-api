import datetime
from typing import Self

from pydantic import BaseModel
from pydantic.functional_validators import field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo

import validation
from ingestion.utils import type_hints
from metrics.api.settings.auth import AUTH_ENABLED
from validation.data_transfer_models.base import (
    IncomingBaseDataModel,
    NonPublicDataSentToPublicIngestionError,
)


class InboundHeadlineSpecificFields(BaseModel):
    """Base data validation object for the lower level fields for headline type data"""

    period_start: datetime.datetime
    period_end: datetime.datetime
    upper_confidence: float | None = None
    embargo: datetime.datetime | None
    metric_value: float
    lower_confidence: float | None = None
    is_public: bool = True

    @field_validator("embargo")
    @classmethod
    def cast_embargo_to_uk_timezone(
        cls, embargo: datetime.datetime
    ) -> datetime.datetime:
        """Casts the inbound `embargo` to the London timezone

        Args:
            embargo: The inbound embargo
                datetime object

        Returns:
            A `datetime` object which has the timezone
            info set to the declared `TIMEZONE` as per
            the main django settings

        """
        return validation.cast_date_to_uk_timezone(date_value=embargo)

    @field_validator("period_start")
    @classmethod
    def cast_period_start_to_uk_timezone(
        cls, period_start: datetime.datetime
    ) -> datetime.datetime:
        """Casts the inbound `period_start` to the London timezone

        Args:
            period_start: The inbound period_start
                datetime object

        Returns:
            A `datetime` object which has the timezone
            info set to the declared `TIMEZONE` as per
            the main django settings

        """
        return validation.cast_date_to_uk_timezone(date_value=period_start)

    @field_validator("period_end")
    @classmethod
    def cast_period_end_to_uk_timezone(
        cls, period_end: datetime.datetime
    ) -> datetime.datetime:
        """Casts the inbound `period_end` to the London timezone

        Args:
            period_end: The inbound period_start
                datetime object

        Returns:
            A `datetime` object which has the timezone
            info set to the declared `TIMEZONE` as per
            the main django settings

        """
        return validation.cast_date_to_uk_timezone(date_value=period_end)

    @field_validator("period_end")
    @classmethod
    def validate_period_dates(
        cls, period_end: datetime.date, validation_info: ValidationInfo
    ) -> datetime.date:
        """Validates the `data` field to check it conforms to the expected rules

        Notes:
            There must be only 1 `InboundHeadlineSpecificFields` model.
            If there is either no data point or multiple data points,
            then the validation checks will fail.

        Args:
            data: The `data` field value being validated

        Returns:
            The input `data` unchanged if
            it has passed the validation checks.

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        input_period_start: datetime.date | None = validation_info.data.get(
            "period_start"
        )
        return validation.validate_period_end(
            period_start=input_period_start, period_end=period_end
        )

    @model_validator(mode="after")
    def validate_confidence_intervals(self) -> Self:
        """Checks that the rules for upper_confidence are followed

        Args:
           self: the model to be validated

        Returns:
             The input unchanged if it has passed the validation
             checks.

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        validation.validate_confidence_intervals(
            upper_confidence=self.upper_confidence,
            lower_confidence=self.lower_confidence,
            metric_value=self.metric_value,
        )
        return self

    @model_validator(mode="after")
    def invalidate_non_public_data_for_public_ingestion(self) -> Self:
        """Checks that if this is a public instance of the product then `is_public=False` data is invalidated."""
        if not AUTH_ENABLED and not self.is_public:
            raise NonPublicDataSentToPublicIngestionError

        return self


class HeadlineDTO(IncomingBaseDataModel):
    data: list[InboundHeadlineSpecificFields]


def _build_headline_dto(
    *,
    source_data: type_hints.INCOMING_DATA_TYPE,
    enriched_specific_fields: list[InboundHeadlineSpecificFields],
) -> HeadlineDTO:
    return HeadlineDTO(
        parent_theme=source_data["parent_theme"],
        child_theme=source_data["child_theme"],
        topic=source_data["topic"],
        metric_group=source_data["metric_group"],
        upper_confidence=source_data.get("upper_confidence"),
        metric=source_data["metric"],
        lower_confidence=source_data.get("lower_confidence"),
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
    *,
    source_data: type_hints.INCOMING_DATA_TYPE,
) -> list[InboundHeadlineSpecificFields]:
    return [
        InboundHeadlineSpecificFields(
            period_start=individual_time_series["period_start"],
            period_end=individual_time_series["period_end"],
            embargo=individual_time_series["embargo"],
            upper_confidence=individual_time_series.get("upper_confidence", None),
            metric_value=individual_time_series["metric_value"],
            lower_confidence=individual_time_series.get("lower_confidence", None),
            is_public=individual_time_series.get("is_public", True),
        )
        for individual_time_series in source_data["data"]
        if individual_time_series["metric_value"] is not None
    ]
