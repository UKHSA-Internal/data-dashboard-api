"""
This file contains access-like (read) functionality for interacting with the database layer.
This shall only include functionality which is used to read from the database.

Specifically, this file contains read database logic for the Core models only.
"""
import datetime
from typing import List, Tuple, Union

from dateutil.relativedelta import relativedelta
from django.db.models import Manager

from metrics.data import type_hints
from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


def get_date_n_months_ago(number_of_months: int = 6) -> datetime.datetime:
    today = datetime.datetime.today()
    n_months_ago: datetime.datetime = today - relativedelta(months=number_of_months)

    return datetime.datetime(year=n_months_ago.year, month=n_months_ago.month, day=1)


def unzip_values(values) -> Tuple[List, List]:
    return zip(*values)


def get_vaccination_uptake_rates(
    topic: str, core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER
) -> List[int]:
    base_name = "latest_vaccination_uptake_"

    autumn_uptake: type_hints.NUMBER = core_time_series_manager.get_latest_metric_value(
        topic=topic, metric_name=f"{base_name}autumn22"
    )

    spring_uptake: type_hints.NUMBER = core_time_series_manager.get_latest_metric_value(
        topic=topic, metric_name=f"{base_name}spring22"
    )

    return [int(spring_uptake), int(autumn_uptake)]


def get_timeseries_metric_values_from_date(
    metric_name: str,
    topic: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> type_hints.DATES_AND_VALUES:
    n_months_ago: datetime.datetime = get_date_n_months_ago()

    queryset = core_time_series_manager.by_topic_metric_for_dates_and_values(
        topic=topic,
        metric_name=metric_name,
        date_from=n_months_ago,
    )

    dates, values = unzip_values(queryset)

    return dates, values


def get_metric_value(
    metric_name: str,
    topic: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> Union[int, float]:
    metric_value: Union[int, float] = core_time_series_manager.get_latest_metric_value(
        topic=topic,
        metric_name=metric_name,
    )

    return metric_value
