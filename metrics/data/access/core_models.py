"""
This file contains access-like (read) functionality for interacting with the database layer.
This shall only include functionality which is used to read from the database.

Specifically, this file contains read database logic for the Core models only.
"""
from typing import Dict, List, Tuple

from django.db.models import Manager, QuerySet

from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


def unzip_values(values) -> Tuple[List, List]:
    """
    Take a list and unzip it

    Args:
        The list of things to unzip

    Returns:
        An unzipped version of the input
    """

    return zip(*values)


def get_month_end_timeseries_metric_values_from_date(
    plot_parameters,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> List[Dict[str, str]]:
    """
    Fetch the month-end timeseries values for the given topic & metric
     Args:
         plot_parameters: The required plot parameters
         core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager
     Returns:
         A dictionary of date:metric_value pairs
    """
    queryset = core_time_series_manager.by_topic_metric_for_dates_and_values(
        topic_name=plot_parameters.topic_name,
        metric_name=plot_parameters.metric_name,
        date_from=plot_parameters.date_from_value,
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

        monthly_data.append({"date": str(dt), "value": metric_value})

    return monthly_data
