"""
This file contains access-like (read) functionality for interacting with the database layer.
This shall only include functionality which is used to read from the database.

Specifically, this file contains read database logic for the API models only.
"""

from typing import List, Union

from django.db.models import Manager, QuerySet

from apiv3.models.api_models import WeeklyTimeSeries

DEFAULT_WEEKLY_TIME_SERIES_MANAGER = WeeklyTimeSeries.objects


def get_weekly_disease_incidence(
    topic: str,
    weekly_time_series_manager: Manager = DEFAULT_WEEKLY_TIME_SERIES_MANAGER,
) -> List[Union[int, float]]:
    """Queries the `WeeklyTimeSeries` (api model) for weekly incidences.

    Note that this function casts the resultant queryset to a list.
    Which will incur the penalty of a db call/ full query execution,
    not just lazy evaluation.

    Args:
        topic: The name of the disease being queried.
            E.g. `Influenza`
        weekly_time_series_manager: The model manager used
            for the `WeeklyTimeSeries`.
            Defaults to `WeeklyTimeSeriesManager`

    Returns:
        List[Union[int, float]]: Flat list of metric values only

    """
    ordered_metric_values_for_topic: QuerySet = (
        weekly_time_series_manager.get_metric_values_for_weekly_positivity_by_topic(
            topic=topic
        )
    )

    return list(ordered_metric_values_for_topic)
