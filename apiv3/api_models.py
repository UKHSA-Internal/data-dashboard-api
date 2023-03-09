"""
For any given API we will require:
 - An API View
 - Flat model generated from the core data
 - Function to generate the flat model from the core data

This file contains the flat models only.
Note that the flat models should only be populated
    via the `generate_weekly_time_series()` function not through any API route.
"""
from django.db import models
from django.db.models import QuerySet

from apiv3 import enums
from apiv3.models import TimeSeries


class WeeklyTimeSeries(models.Model):
    theme = models.CharField(max_length=30)
    sub_theme = models.CharField(max_length=30)
    topic = models.CharField(max_length=30)

    geography_type = models.CharField(max_length=30)
    geography = models.CharField(max_length=30)

    metric = models.CharField(max_length=30)

    stratum = models.CharField(max_length=30)
    year = models.IntegerField()
    epiweek = models.IntegerField()
    start_date = models.DateField(max_length=30)

    metric_value = models.FloatField(max_length=30)

    def __str__(self):
        return f"Data for {self.start_date}, metric '{self.metric}', stratum '{self.stratum}', value: {self.metric_value}"


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
    all_core_weekly_time_series: QuerySet = time_series_manager.filter(
        period=enums.TimePeriod.Weekly.value
    )

    models_to_be_saved = []
    for core_weekly_time_series in all_core_weekly_time_series:
        core_weekly_time_series: TimeSeries

        flat_weekly_time_series = WeeklyTimeSeries(
            theme=core_weekly_time_series.metric.topic.sub_theme.theme.name,
            sub_theme=core_weekly_time_series.metric.topic.sub_theme.name,
            topic=core_weekly_time_series.metric.topic.name,
            geography=core_weekly_time_series.geography.name,
            geography_type=core_weekly_time_series.geography.geography_type.name,
            metric=core_weekly_time_series.metric.name,
            stratum=core_weekly_time_series.stratum.name,
            year=core_weekly_time_series.year,
            epiweek=core_weekly_time_series.epiweek,
            start_date=core_weekly_time_series.start_date,
            metric_value=core_weekly_time_series.metric_value,
        )
        models_to_be_saved.append(flat_weekly_time_series)

    weekly_time_series_manager.bulk_create(objs=models_to_be_saved)
