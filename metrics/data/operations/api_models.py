"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

Specifically, this file contains write database logic for the API models only.
"""

from django.db import models
from django.db.models import QuerySet

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_API_TIME_SERIES_MANAGER = APITimeSeries.objects


def generate_api_time_series(
    core_time_series_manager: models.Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    api_time_series_manager: models.Manager = DEFAULT_API_TIME_SERIES_MANAGER,
) -> None:
    """Queries the core `CoreTimeSeries` models and populates the flat `APITimeSeries`

    Args:
        core_time_series_manager: The model Manager associated with the `CoreTimeSeries` model.
            Defaults to the native `CoreTimeSeries` manager.
        api_time_series_manager: The model Manager associated with the `APITimeSeries` model.
            Defaults to the native `APITimeSeries` manager.

    Returns:
        None

    """
    all_core_time_series: QuerySet = core_time_series_manager.all_related()

    models_to_be_saved = []
    for core_time_series in all_core_time_series:
        flat_time_series: APITimeSeries = create_api_time_series_from_core_time_series(
            core_time_series=core_time_series
        )
        models_to_be_saved.append(flat_time_series)

    api_time_series_manager.bulk_create(objs=models_to_be_saved)


def create_api_time_series_from_core_time_series(
    core_time_series: CoreTimeSeries,
) -> APITimeSeries:
    return APITimeSeries(
        period=core_time_series.period,
        theme=core_time_series.metric.topic.sub_theme.theme.name,
        sub_theme=core_time_series.metric.topic.sub_theme.name,
        topic=core_time_series.metric.topic.name,
        geography_type=core_time_series.geography.geography_type.name,
        geography=core_time_series.geography.name,
        metric=core_time_series.metric.name,
        stratum=core_time_series.stratum.name,
        sex=core_time_series.sex,
        year=core_time_series.year,
        epiweek=core_time_series.epiweek,
        dt=core_time_series.dt,
        metric_value=core_time_series.metric_value,
    )
