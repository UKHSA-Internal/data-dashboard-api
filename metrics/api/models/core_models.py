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
from metrics.api.managers.core_models.time_series import TimeSeriesManager


class Theme(models.Model):
    name = models.CharField(max_length=30)
    created_dt = models.DateTimeField(default=timezone.now)


class SubTheme(models.Model):
    name = models.CharField(max_length=30)
    theme = models.ForeignKey(to=Theme, on_delete=models.SET_NULL, null=True)
    created_dt = models.DateTimeField(default=timezone.now)


class Topic(models.Model):
    name = models.CharField(max_length=30)
    sub_theme = models.ForeignKey(to=SubTheme, on_delete=models.SET_NULL, null=True)


class GeographyType(models.Model):
    name = models.CharField(max_length=30)


class Geography(models.Model):
    name = models.CharField(max_length=30)
    geography_type = models.ForeignKey(
        to=GeographyType, on_delete=models.SET_NULL, null=True
    )


class Metric(models.Model):
    name = models.CharField(max_length=30)
    rounding = models.CharField(max_length=100)
    topic = models.ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)


class Stratum(models.Model):
    name = models.CharField(max_length=30)


class TimeSeries(models.Model):
    """

    Notes:
        `metric_value` will always be pre-calculated before persisting in the db.
        Therefore, values may be rounded to 1 d.p but these figures should not be used for onward calculations.
        These values are to be used solely for dashboard visualisation and API egress

    """

    epiweek = models.IntegerField()
    metric_value = models.DecimalField(max_digits=11, decimal_places=1)
    start_date = models.DateField()
    year = models.IntegerField()

    period = models.CharField(max_length=1, choices=TimePeriod.choices())

    stratum = models.ForeignKey(to=Stratum, on_delete=models.SET_NULL, null=True)
    metric = models.ForeignKey(to=Metric, on_delete=models.SET_NULL, null=True)
    geography = models.ForeignKey(to=Geography, on_delete=models.SET_NULL, null=True)

    objects = TimeSeriesManager()
