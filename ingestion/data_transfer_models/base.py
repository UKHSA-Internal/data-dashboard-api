import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from ingestion.data_transfer_models import validation
from ingestion.utils import enums


class MissingFieldError(Exception):
    def __init__(self, *, field: str):
        message = f"`{field}` field is missing from the inbound source data"
        super().__init__(message)


class IncomingBaseDataModel(BaseModel):
    """Base data validation object for the upper level/common fields"""

    parent_theme: str
    child_theme: str
    topic: enums.Topic
    metric_group: enums.DataSourceFileType
    metric: str
    geography_type: enums.GeographyType
    geography: str
    geography_code: str = Field(max_length=9, min_length=3)
    age: str
    sex: str
    stratum: str
    refresh_date: datetime.datetime

    model_config = ConfigDict(use_enum_values=True)

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

    @field_validator("geography_code")
    @classmethod
    def validate_geography_code(
        cls, geography_code: str, validation_info: ValidationInfo
    ) -> str:
        """Validates the `geography_code` value to check it conforms to an allowable structure

        Args:
            geography_code: The `geography_code` value
                being validated
            validation_info: An enriched `ValidationInfo` instance
                provided by the pydantic model, this gives us
                the rest of the payload to the model initialization.
                From this, the `geography_code` is extracted,
                so it can be used in the validation checks

        Returns:
            The provided `geography_code` unchanged if
            it has passed the validation checks.

        Raises:
            `ValidationError`: If any of the validation checks fail

        """
        input_geography_type: str = validation_info.data.get("geography_type")
        return validation.validate_geography_code(
            geography_code=geography_code,
            geography_type=input_geography_type,
        )
