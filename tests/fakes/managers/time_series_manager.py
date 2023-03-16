from metrics.api import enums
from metrics.api.managers.core_models.time_series import TimeSeriesManager


class FakeTimeSeriesManager(TimeSeriesManager):
    """
    A fake version of the `TimeSeriesManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, time_series, **kwargs):
        self.time_series = time_series
        super().__init__(**kwargs)

    def filter_weekly(self):
        return [
            x for x in self.time_series if x.period == enums.TimePeriod.Weekly.value
        ]
