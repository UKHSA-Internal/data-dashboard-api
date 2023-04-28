"""
This file contains access-like (read) functionality for interacting with the database layer.
This shall only include functionality which is used to read from the database.

Specifically, this file contains read database logic for the Core models only.
"""
import datetime
from typing import Dict, List, Tuple, Union

from dateutil.relativedelta import relativedelta
from django.db.models import Manager, QuerySet

from metrics.data import type_hints
from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


def get_date_n_months_ago_from_timestamp(
    datetime_stamp: datetime.datetime, number_of_months: int = 6
) -> datetime.datetime:
    """
    Get the 1st day of the month x months in the past

    Args:
        datetime_stamp: The datetime stamp to calculate from.
        number_of_months: the number of months to go back. Default 6

    Returns:
        A datetime of the fist day of the month x months ago
    """

    n_months_ago: datetime.datetime = datetime_stamp - relativedelta(
        months=number_of_months
    )

    return datetime.datetime(year=n_months_ago.year, month=n_months_ago.month, day=1)


def unzip_values(values) -> Tuple[List, List]:
    """
    Take a list and unzip it

    Args:
        The list of things to unzip

    Returns:
        An unzipped version of the input
    """

    return zip(*values)


def get_vaccination_uptake_rates(
    topic: str, core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER
) -> List[int]:
    """
    Fetch the vaccine uptake rates for autumn and spring 2022

    Args:
        topic: The topic (eg. COVID-19) we want the vaccine uptake for
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The two rates as a list.
    """

    base_name = "latest_vaccinations_uptake_"

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
    """
    Fetch the timeseries for the given topic & metric

    Args:
        metric_name: The required metric (eg. new_admissions_7days)
        topic: The required topic (eg. COVID-19)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The timeseries seperated into two lists. Dates in one, values in the other
    """
    today = datetime.datetime.today()
    n_months_ago: datetime.datetime = get_date_n_months_ago_from_timestamp(
        datetime_stamp=today
    )

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
    """
    Fetch the latest metric value

    Args:
        metric_name: The required metric (eg. new_admissions_7days)
        topic: The required topic (eg. COVID-19)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The latest value for the given metric and topic
    """

    metric_value: Union[int, float] = core_time_series_manager.get_latest_metric_value(
        topic=topic,
        metric_name=metric_name,
    )

    return metric_value


def get_month_end_timeseries_metric_values_from_date(
    metric_name: str,
    topic: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> List[Dict[str, str]]:
    """
    Fetch the month-end timeseries values for the given topic & metric
     Args:
         metric_name: The required metric (eg. new_cases_daily)
         topic: The required topic (eg. COVID-19)
         core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager
     Returns:
         A dictionary of date:metric_value pairs
    """
    today = datetime.datetime.today()
    n_months_ago: datetime.datetime = get_date_n_months_ago_from_timestamp(
        datetime_stamp=today
    )

    queryset = core_time_series_manager.by_topic_metric_for_dates_and_values(
        topic=topic,
        metric_name=metric_name,
        date_from=n_months_ago,
    )

    months: QuerySet = queryset.dates("dt", kind="month")

    monthly_data = []
    for month in months:
        dt, metric_value = (
            queryset.filter(
                dt__year=month.year,
                dt__month=month.month,
            )
            .order_by("dt")
            .last()
        )

        monthly_data.append({"date": str(dt), "value": str(metric_value)})

    return monthly_data
