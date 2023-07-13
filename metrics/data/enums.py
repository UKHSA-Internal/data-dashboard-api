from enum import Enum


class TimePeriod(Enum):
    Annual = "A"
    Quarterly = "Q"
    Monthly = "M"
    Fortnightly = "F"
    Weekly = "W"
    Daily = "D"

    @classmethod
    def choices(cls):
        return tuple((time_period.value, time_period.value) for time_period in cls)
