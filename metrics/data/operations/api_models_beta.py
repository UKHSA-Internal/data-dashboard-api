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


def generate_api_time_series_beta(
    core_time_series_manager: models.manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    api_time_series_manger: models.manager = DEFAULT_API_TIME_SERIES_MANAGER,
    batch_size: int = 100,
) -> None:
    """Queries the core 'CoreTimeSeries' models and populates the flat 'APITimeSeries'

    Notes:
        If there are any existing 'APITimeSeries' records, then this will return early.
        And no additional records will be added to the 'APITimeSeries table.

    Args:
        core_time_series_manager: the model manager for the 'CoreTimeSeries' model.
            defaults to the native 'CoreTimeSeries' manager.
        api_time_series_manger: the model manager for the 'APITimeSeries' model.
            defaults to the native 'APITimeSeries' manager.
        batch_size: controls the number of objects created in a single query.
            defaults to 100.

    Returns:
        None

    """
    if api_time_series_manger.exists():
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

    api_time_series_manger.bulk_create(objs=models_to_be_saved, batch_size=batch_size)


def create_api_time_series_from_core_time_series(
    core_time_series: CoreTimeSeries,
) -> APITimeSeries:
    return APITimeSeries(
        theme=core_time_series.metric.topic.sub_theme.theme.name,
        sub_theme=core_time_series.metric.topic.sub_theme.name,
        topic=core_time_series.metric.topic.name,
        metric=core_time_series.metric.name,
        metric_group=core_time_series.metric.metric_group.name,
        metric_frequency=core_time_series.metric_frequency,
        geography_type=core_time_series.geography.geography_type.name,
        geography=core_time_series.geography.name,
        geography_code=core_time_series.geography.geography_code,
        age=core_time_series.age,
        sex=core_time_series.sex,
        stratum=core_time_series.stratum.name,
        epiweek=core_time_series.epiweek,
        date=core_time_series.date,
        metric_value=core_time_series.metric_value,
        refresh_date=core_time_series.refresh_date,
        month=core_time_series.month,
        year=core_time_series.year,
    )
