import datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo

import validation
from validation import enums
from validation.metrics_interface.interface import MetricsAPIInterface


class NonPublicDataSentToPublicIngestionError(ValueError):
    def __init__(self):
        message = "Inbound data with `is_public=False` cannot be ingested when `AUTH_ENABLED` is false"
        super().__init__(message)


class MissingFieldError(Exception):
    def __init__(self, *, field: str):
        message = f"`{field}` field is missing from the inbound source data"
        super().__init__(message)


class IncomingBaseDataModel(BaseModel):
    """Base data validation object for the upper level/common fields"""

    parent_theme: enums.ParentTheme
    child_theme: str
    topic: str
    metric_group: MetricsAPIInterface.get_datasource_enum()
    metric: str
    geography_type: enums.GeographyType
    geography: str
    geography_code: str = Field(max_length=9, min_length=3)
    age: str
    sex: str
    stratum: str
    refresh_date: datetime.datetime

    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def validate_child_theme_belongs_to_primary_theme(self) -> Self:
        """Validates the `child_theme` against the provided `parent_theme`"""

        validation.validate_child_theme(
            child_theme=self.child_theme,
            parent_theme=self.parent_theme,
        )

        return self

    @model_validator(mode="after")
    def validate_topic_against_child_theme(self) -> Self:
        """Validates the `topic` against the provided `child_theme`"""

        validation.validate_topic(topic=self.topic, child_theme=self.child_theme)

        return self

    @field_validator("sex")
    @classmethod
    def cast_sex_to_an_expected_value(cls, sex: str) -> str:
        """Casts the `sex` value to one of the expected values

        Notes:
            Expected values are one of the following:
            1) "all"    - All genders with no filtering applied
            2) "f"      - Females
            3) "m"      - Males

        Returns:
            A string representation of the parsed sex value

        """
        sex_options = {"male": "m", "female": "f", "all": "all"}
        return sex_options.get(sex.lower(), "all")

    @field_validator("age")
    @classmethod
    def validate_age(cls, age: str) -> str:
        """Validates the `age` value to check it conforms to an allowable structure

        Notes:
            The `age` value must be one of the following:
                - The literal string "all"
                - An age banding like `00-04`
                    which must have 2 double-digit numbers
                - An age greater than like `85+`
                    which must have 1 double-digit number
                    followed by the `+` operator

        Args:
            age: The `age` value being validated

        Returns:
            The provided `age` unchanged if
            it has passed the validation checks.

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        return validation.validate_age(age=age)

    @model_validator(mode="after")
    def validate_geography_code(self) -> Self:
        """Validates the `geography_code` value to check it conforms to an allowable structure

        Returns:
            The current model instance

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        validation.validate_geography_code(
            geography_code=self.geography_code,
            geography_type=self.geography_type,
            geography=self.geography,
        )
        return self

    @model_validator(mode="after")
    def validate_deprecated_geography(self) -> Self:
        """Validates the geography to check it has not been deprecated

        Returns:
            The current model instance

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        validation.validate_deprecated_geographies(
            geography_code=self.geography_code,
            geography_type=self.geography_type,
            geography_name=self.geography,
        )
        return self

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, metric: str, validation_info: ValidationInfo) -> str:
        """Validates the `metric` value to check it conforms to an allowable structure

        Notes:
            The `metric` name must contain
            the `metric_group` value from the payload

        Args:
            metric: The `metric` name being validated
            validation_info: An enriched `ValidationInfo` instance
                provided by the pydantic model, this gives us
                the rest of the payload to the model initialization.
                From this, the `metric_group` is extracted,
                so it can be used in the validation checks

        Returns:
            The provided `metric` unchanged if
            it has passed the validation checks.

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        input_metric_group: str | None = validation_info.data.get("metric_group")
        input_topic: str | None = validation_info.data.get("topic")
        return validation.validate_metric(
            metric=metric,
            metric_group=input_metric_group,
            topic=input_topic,
        )

    @field_validator("refresh_date")
    @classmethod
    def cast_refresh_date_to_uk_timezone(
        cls, refresh_date: datetime.datetime
    ) -> datetime.datetime:
        """Casts the inbound `refresh_date` to the London timezone

        Args:
            refresh_date: The inbound refresh date
                datetime object

        Returns:
            A `datetime` object which has the timezone
            info set to the declared `TIMEZONE` as per
            the main django settings

        """
        return validation.cast_date_to_uk_timezone(date_value=refresh_date)
