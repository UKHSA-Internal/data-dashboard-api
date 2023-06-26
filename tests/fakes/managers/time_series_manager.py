import datetime
from typing import Optional, Union

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
        self,
        topic_name: str,
        metric_name: str,
        date_from: datetime.datetime,
    ):
        return [
            (time_series.dt, time_series.metric_value)
            for time_series in self.time_series
            if time_series.metric.topic_name.name == topic_name
            if time_series.metric.name == metric_name
        ]

    def get_count(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: Union[datetime.datetime, str],
    ) -> int:
        date_from = _convert_string_to_date(date_string=date_from)

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

    def filter_for_x_and_y_values(
        self,
        x_axis: str,
        y_axis: str,
        topic_name: str,
        metric_name: str,
        date_from: datetime.date,
        geography_name: Optional[str] = None,
        geography_type_name: Optional[str] = None,
        stratum_name: Optional[str] = None,
        sex: Optional[str] = None,
    ):
        date_from = _convert_string_to_date(date_string=date_from)

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

        if sex:
            filtered_time_series = [x for x in filtered_time_series if x.sex == sex]

        return [
            (time_series.dt, time_series.metric_value)
            for time_series in filtered_time_series
        ]

    def exists(self) -> bool:
        return bool(self.time_series)


def _convert_string_to_date(date_string: str) -> datetime.date:
    """Convenience function to convert date strings to `datetime.date` objects.

    Notes:
        The Django ORM supports dates as strings or as `datetime.date` objects.
        This function is used to mimic that behavior.

    Args:
        date_string (str): The date string to convert.

    Returns:
        `datetime.date: The converted date as an object.

    """
    if type(date_string) is str:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

    if type(date_string) is datetime.datetime:
        return date_string.date()

    return date_string
