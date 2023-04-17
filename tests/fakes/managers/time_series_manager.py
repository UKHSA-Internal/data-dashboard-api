import datetime

from metrics.data import enums
from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager


class FakeCoreTimeSeriesManager(CoreTimeSeriesManager):
    """
    A fake version of the `CoreTimeSeriesManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, time_series, **kwargs):
        self.time_series = time_series
        super().__init__(**kwargs)

    def filter_weekly(self):
        return [
            x for x in self.time_series if x.period == enums.TimePeriod.Weekly.value
        ]

    def all_related(self):
        return [x for x in self.time_series]

    def by_topic_metric_for_dates_and_values(
        self, topic: str, metric_name: str, date_from: datetime.datetime
    ):
        return [
            (time_series.dt, time_series.metric_value)
            for time_series in self.time_series
        ]

    def get_count(
        self, topic: str, metric_name: str, date_from: datetime.datetime
    ) -> int:
        filtered_for_metric_topic_and_date = [
            x
            for x in self.time_series
            if x.metric.topic.name == topic
            if x.metric.name == metric_name
            if x.dt >= date_from
        ]
        return len(filtered_for_metric_topic_and_date)
