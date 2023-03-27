"""
This file contains access-like (read) functionality for interacting with the database layer.
This shall only include functionality which is used to read from the database.

Specifically, this file contains read database logic for the API models only.
"""
import datetime
from typing import List, Tuple, Union

from dateutil.relativedelta import relativedelta
from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


def get_date_six_months_ago():
    today = datetime.datetime.today()
    return today - relativedelta(months=6)


def _unzip_into_lists(result) -> Tuple[List, List]:
    return zip(*result)


def get_vaccination_uptake_rates(
    topic: str, core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER
):
    base_name = "latest_vaccination_uptake_"

    autumn_uptake = core_time_series_manager.get_latest_metric_value(
        topic=topic, metric=f"{base_name}autum22"
    )

    spring_uptake = core_time_series_manager.get_latest_metric_value(
        topic=topic, metric=f"{base_name}spring22"
    )

    return [int(spring_uptake), int(autumn_uptake)]


def get_hospital_admission_rates(
    topic: str, core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER
):
    six_months_ago = get_date_six_months_ago()

    queryset = core_time_series_manager.by_topic_metric_for_dates_and_values(
        topic=topic,
        metric="weekly_hospital_admission_rate",
        date_from=six_months_ago,
    )

    dates, values = _unzip_into_lists(queryset)

    return dates, values


def get_weekly_disease_incidence(
    topic: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> List[Union[int, float]]:
    """Queries the `APITimeSeries` (api model) for weekly incidences.

    Note that this function casts the resultant queryset to a list.
    Which will incur the penalty of a db call/ full query execution,
    not just lazy evaluation.

    Args:
        topic: The name of the disease being queried.
            E.g. `Influenza`
        core_time_series_manager: The model manager used
            for the `CoreTimeSeries`.
            Defaults to `CoreTimeSeriesManager`

    Returns:
        List[Union[int, float]]: Flat list of metric values only

    """
    six_months_ago = get_date_six_months_ago()
    queryset = core_time_series_manager.by_topic_metric_for_dates_and_values(
        topic=topic,
        metric="weekly_positivity",
        date_from=six_months_ago,
    )
    dates, values = _unzip_into_lists(queryset)

    return dates, values
