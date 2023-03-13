"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

Specifically, this file contains write database logic for the API models only.
"""

from django.db import models
from django.db.models import QuerySet

from apiv3 import enums
from apiv3.models.api_models import WeeklyTimeSeries
from apiv3.models.core_models import TimeSeries

DEFAULT_TIME_SERIES_MANAGER = TimeSeries.objects
DEFAULT_WEEKLY_TIME_SERIES_MANAGER = WeeklyTimeSeries.objects


def generate_weekly_time_series(
    time_series_manager: models.Manager = DEFAULT_TIME_SERIES_MANAGER,
    weekly_time_series_manager: models.Manager = DEFAULT_WEEKLY_TIME_SERIES_MANAGER,
) -> None:
    """Queries the core `TimeSeries` models and populates the flat `WeeklyTimeSeries`

    Args:
        time_series_manager: The model Manager associated with the `TimeSeries` model.
            Defaults to the native `TimeSeries` manager.
        weekly_time_series_manager: The model Manager associated with the `WeeklyTimeSeries` model.
            Defaults to the native `WeeklyTimeSeries` manager.

    Returns:
        None

    """
    all_core_time_series: QuerySet = time_series_manager.filter(
        period=enums.TimePeriod.Weekly.value
    )

    models_to_be_saved = []
    for core_time_series in all_core_time_series:
        core_time_series: TimeSeries

        flat_weekly_time_series = WeeklyTimeSeries(
            theme=core_time_series.metric.topic.sub_theme.theme.name,
            sub_theme=core_time_series.metric.topic.sub_theme.name,
            topic=core_time_series.metric.topic.name,
            geography=core_time_series.geography.name,
            geography_type=core_time_series.geography.geography_type.name,
            metric=core_time_series.metric.name,
            stratum=core_time_series.stratum.name,
            year=core_time_series.year,
            epiweek=core_time_series.epiweek,
            start_date=core_time_series.start_date,
            metric_value=core_time_series.metric_value,
        )
        models_to_be_saved.append(flat_weekly_time_series)

    weekly_time_series_manager.bulk_create(objs=models_to_be_saved)
