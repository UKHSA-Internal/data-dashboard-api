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
    theme: str = "",
    sub_theme: str = "",
    topic: str = "",
    metric: str = "",
    metric_group: str = "",
    metric_frequency: str = "",
    refresh_date: str = "",
) -> APITimeSeries:
    """Creates a new `APITimeSeries` object from the given `core_time_series`

    Notes:
        Additional fields can be provided to pass directly to the `APITimeSeries`.
        This is to introduce a small optimization.
        Files are ingested on a per-metric basis.
        So we can say for each file, a group of fields will be the same.
        We can take advantage of this and continuously pass them to each
        record being created as per the file being ingested without having
        to pull those fields again from the corresponding `CoreTimeSeries`
        for each individual `APITimeSeries`

    Args:
        core_time_series: The `CoreTimeSeries` from which to produce
            the flattened/de-normalized version of with an `APITimeSeries`
        theme: The value of the largest topical subgroup
            E.g. "infectious_disease"
            If not provided, the value will be taken
            from the `Theme` object related to the `CoreTimeSeries`
        sub_theme: The value of the topical subgroup
            E.g. "respiratory"
            If not provided, the value will be taken
            from the `SubTheme` object `CoreTimeSeries`
        topic: The name of the disease/threat
            E.g. "COVID-19"
            If not provided, the value will be taken
            from the `Topic` object related to the `CoreTimeSeries`
        metric: The name of the metric associated with the timeseries
            E.g. "COVID-19_cases_casesByDay"
            If not provided, the value will be taken
            from the `Metric` object related to the `CoreTimeSeries`
        metric_group: The grouping in which the `metric` sits under.
            E.g. "cases"
            If not provided, the value will be taken
            from the `MetricGroup` object related to the `CoreTimeSeries`
        metric_frequency: The smallest time period for which
            a metric is reported.
            E.g. "W" for "Weekly"
            If not provided, the value will be taken from the related `CoreTimeSeries`
        refresh_date: The date at which the `metric` was last updated
            E.g. "2023-08-03"
            If not provided, the value will be taken from the related `CoreTimeSeries`

    Returns:
        An `APITimeSeries` instance which mirrors
        the given `CoreTimeSeries` instance

    """
    return APITimeSeries(
        # Fields which can be provided ahead of time
        theme=theme or core_time_series.metric.topic.sub_theme.theme.name,
        sub_theme=sub_theme or core_time_series.metric.topic.sub_theme.name,
        topic=topic or core_time_series.metric.topic.name,
        metric=metric or core_time_series.metric.name,
        metric_group=metric_group or core_time_series.metric.metric_group.name,
        metric_frequency=metric_frequency or core_time_series.metric_frequency,
        refresh_date=refresh_date or core_time_series.refresh_date,
        # Fields always taken from the `core_time_series`
        geography_type=core_time_series.geography.geography_type.name,
        geography=core_time_series.geography.name,
        geography_code=core_time_series.geography.geography_code,
        age=core_time_series.age,
        sex=core_time_series.sex,
        stratum=core_time_series.stratum.name,
        date=core_time_series.date,
        year=core_time_series.year,
        month=core_time_series.month,
        epiweek=core_time_series.epiweek,
        metric_value=core_time_series.metric_value,
    )
