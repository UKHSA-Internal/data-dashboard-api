import datetime
from decimal import Decimal

from pydantic.main import BaseModel


class Headline(BaseModel):
    metric_value: Decimal
    period_end: datetime.datetime
