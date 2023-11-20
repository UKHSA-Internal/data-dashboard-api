import datetime

from pydantic import BaseModel


class IncomingTimeSeriesValidation(BaseModel):
    """Base data validation object for the lower level fields for time series type data"""

    epiweek: int
    date: datetime.date
    embargo: datetime.datetime
    metric_value: float
