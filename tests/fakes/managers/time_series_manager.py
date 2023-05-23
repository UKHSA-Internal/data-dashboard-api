import datetime
from typing import Optional

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
        self, topic_name: str, metric_name: str, date_from: datetime.datetime
    ):
        return [
            (time_series.dt, time_series.metric_value)
            for time_series in self.time_series
            if time_series.metric.topic_name.name == topic_name
            if time_series.metric.name == metric_name
        ]

    def get_count(
        self, topic_name: str, metric_name: str, date_from: datetime.datetime
    ) -> int:
        filtered_for_metric_topic_and_date = [
            x
            for x in self.time_series
            if x.metric.topic.name == topic_name
            if x.metric.name == metric_name
            if x.dt >= date_from
        ]
        return len(filtered_for_metric_topic_and_date)

    def get_latest_metric_value(
        self, topic_name: str, metric_name: str
    ) -> Optional[float]:
        try:
            core_time_series = next(
                core_time_series
                for core_time_series in self.time_series
                if core_time_series.metric.topic.name == topic_name
                if core_time_series.metric.name == metric_name
            )
        except StopIteration:
            return None
        return core_time_series.metric_value

    def filter_for_dates_and_values(
        self,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        geography_name: Optional[str] = None,
        geography_type_name: Optional[str] = None,
        stratum_name: Optional[str] = None,
    ):
        filtered_time_series = [
            time_series
            for time_series in self.time_series
            if time_series.metric.topic.name == topic_name
            if time_series.metric.name == metric_name
            if time_series.dt > date_from
        ]
        if geography_name:
            filtered_time_series = [
                x for x in filtered_time_series if x.geography.name == geography_name
            ]

        if geography_type_name:
            filtered_time_series = [
                x
                for x in filtered_time_series
                if x.geography.geography_type.name == geography_name
            ]

        if stratum_name:
            filtered_time_series = [
                x for x in filtered_time_series if x.stratum.name == stratum_name
            ]

        return [
            (time_series.dt, time_series.metric_value)
            for time_series in filtered_time_series
        ]
