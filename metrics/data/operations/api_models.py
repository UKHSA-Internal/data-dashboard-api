"""
This file contains operation-like (write) functionality for interacting with the database layer.
This shall only include functionality which is used to write to the database.

Specifically, this file contains write database logic for the API models only.
"""
import logging

from django.db import models
from django.db.models import QuerySet

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_API_TIME_SERIES_MANAGER = APITimeSeries.objects

logger = logging.getLogger(__name__)


def generate_api_time_series(
    core_time_series_manager: models.Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    api_time_series_manager: models.Manager = DEFAULT_API_TIME_SERIES_MANAGER,
    batch_size: int = 100,
) -> None:
    """Queries the core `CoreTimeSeries` models and populates the flat `APITimeSeries`

    Notes:
        If there are any existing `APITimeSeries` records, then this will return early.
        And no additional records will be added to the `APITimeSeries` table.

    Args:
        core_time_series_manager: The model Manager associated with the `CoreTimeSeries` model.
            Defaults to the native `CoreTimeSeries` manager.
        api_time_series_manager: The model Manager associated with the `APITimeSeries` model.
            Defaults to the native `APITimeSeries` manager.
        batch_size: Controls the number of objects created
            in a single query. Defaults to 100.

    Returns:
        None

    """
    if api_time_series_manager.exists():
        logger.info(
            "API Time Series table has existing records. Skipping duplicate record generation."
        )
        return

    all_core_time_series: QuerySet = core_time_series_manager.all_related()

    models_to_be_saved = []
    for core_time_series in all_core_time_series:
        flat_time_series: APITimeSeries = create_api_time_series_from_core_time_series(
            core_time_series=core_time_series
        )
        models_to_be_saved.append(flat_time_series)

    api_time_series_manager.bulk_create(objs=models_to_be_saved, batch_size=batch_size)


def create_api_time_series_from_core_time_series(
    core_time_series: CoreTimeSeries,
) -> APITimeSeries:
    return APITimeSeries(
        period=core_time_series.metric_frequency,
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
        dt=core_time_series.date,
        metric_value=core_time_series.metric_value,
    )
