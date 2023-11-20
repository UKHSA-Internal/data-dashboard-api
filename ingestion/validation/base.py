import datetime

from pydantic import BaseModel, Field

from ingestion.file_ingestion import DataSourceFileType


class IncomingBaseValidation(BaseModel):
    """Base data validation object for the upper level fields"""

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
