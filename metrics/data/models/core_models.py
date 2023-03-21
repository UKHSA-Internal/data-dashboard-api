"""
For any given API we will require:
 - An API View
 - Flat model generated from the core data
 - Function to generate the flat model from the core data models

This file contains the core models only.
The core models should be populated via data ingress (file uploads)
"""

from django.db import models
from django.utils import timezone

from metrics.api.enums import TimePeriod
from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager

CHAR_COLUMN_MAX_CONSTRAINT: int = 50


class Theme(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    created_dt = models.DateTimeField(default=timezone.now)


class SubTheme(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    theme = models.ForeignKey(to=Theme, on_delete=models.SET_NULL, null=True)
    created_dt = models.DateTimeField(default=timezone.now)


class Topic(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sub_theme = models.ForeignKey(to=SubTheme, on_delete=models.SET_NULL, null=True)


class GeographyType(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)


class Geography(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography_type = models.ForeignKey(
        to=GeographyType, on_delete=models.SET_NULL, null=True
    )


class Metric(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    rounding = models.CharField(max_length=100)
    topic = models.ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)


class Stratum(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)


class CoreTimeSeries(models.Model):
    period = models.CharField(
        max_length=1,
        choices=TimePeriod.choices(),
    )
    geography = models.ForeignKey(
        to=Geography,
        on_delete=models.SET_NULL,
        null=True,
    )
    metric = models.ForeignKey(
        to=Metric,
        on_delete=models.SET_NULL,
        null=True,
    )
    stratum = models.ForeignKey(
        to=Stratum,
        on_delete=models.SET_NULL,
        null=True,
    )
    sex = models.CharField(
        max_length=3,
        null=True,
    )
    dt = models.DateField()
    metric_value = models.DecimalField(
        max_digits=11,
        decimal_places=1,
    )

    objects = CoreTimeSeriesManager()
