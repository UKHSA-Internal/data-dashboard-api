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

from metrics.data.managers.api_models.time_series import APITimeSeriesManager

CHAR_COLUMN_MAX_CONSTRAINT: int = 50


class APITimeSeries(models.Model):
    period = models.CharField(max_length=1)

    theme = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sub_theme = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    topic = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography_type = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    metric = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    stratum = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sex = models.CharField(max_length=3, null=True)
    dt = models.DateField()
    metric_value = models.FloatField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = APITimeSeriesManager()

    def __str__(self):
        return f"Data for {self.dt}, metric '{self.metric}', stratum '{self.stratum}', value: {self.metric_value}"
