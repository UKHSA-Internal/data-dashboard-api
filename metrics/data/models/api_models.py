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

from metrics.data.managers.api_models.weekly_time_series import WeeklyTimeSeriesManager


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

    objects = WeeklyTimeSeriesManager()

    def __str__(self):
        return f"Data for {self.start_date}, metric '{self.metric}', stratum '{self.stratum}', value: {self.metric_value}"
