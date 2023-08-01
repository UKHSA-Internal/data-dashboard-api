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
from metrics.data.models.constants import (
    CHAR_COLUMN_MAX_CONSTRAINT,
    GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT,
    PERIOD_MAX_CHAR_CONSTRAINT,
    SEX_MAX_CHAR_CONSTRAINT,
)


class APITimeSeries(models.Model):
    period = models.CharField(max_length=PERIOD_MAX_CHAR_CONSTRAINT)

    age = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT, null=True)
    month = models.PositiveSmallIntegerField(null=True)
    refresh_date = models.DateField(null=True)
    geography_code = models.CharField(
        max_length=GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT, null=True
    )
    metric_group = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT, null=True)
    theme = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sub_theme = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    topic = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography_type = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    metric = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    stratum = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sex = models.CharField(max_length=SEX_MAX_CHAR_CONSTRAINT, null=True)
    year = models.PositiveSmallIntegerField()
    epiweek = models.PositiveSmallIntegerField()
    date = models.DateField()
    metric_value = models.FloatField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = APITimeSeriesManager()

    def __str__(self):
        return f"{self.__class__.__name__} for {self.date}, metric '{self.metric}', stratum '{self.stratum}', value: {self.metric_value}"
