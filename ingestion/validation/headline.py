import datetime

from pydantic import BaseModel


class IncomingHeadlineValidation(BaseModel):
    """Base data validation object for the lower level fields for headline type data"""

    period_start: datetime.date
    period_end: datetime.date
    embargo: datetime.datetime
    metric_value: float
