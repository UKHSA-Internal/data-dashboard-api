import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ingestion.utils.enums import DataSourceFileType


class MissingFieldError(Exception):
    def __init__(self, field: str):
        message = f"`{field}` field is missing from the inbound source data"
        super().__init__(message)


class IncomingBaseDataModel(BaseModel):
    """Base data validation object for the upper level/common fields"""

    parent_theme: str
    child_theme: str
    topic: str
    metric_group: DataSourceFileType
    metric: str
    geography_type: str
    geography: str
    geography_code: str = Field(max_length=9, min_length=3)
    age: str
    sex: str
    stratum: str
    refresh_date: datetime.date

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("sex")
    @classmethod
    def cast_sex_to_an_expected_value(cls, sex: str):
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
