import datetime

from pydantic import BaseModel, ConfigDict, Field

from ingestion.file_ingestion import DataSourceFileType


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
