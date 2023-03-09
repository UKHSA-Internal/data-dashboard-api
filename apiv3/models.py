"""
For any given API we will require:
 - An API View
 - Flat model generated from the core data
 - Function to generate the flat model from the core data models

This file contains the core models only.
The core models should be populated via data ingress (file uploads)
"""
import io
from datetime import datetime
from typing import List

from django.db import models
from django.utils import timezone

from apiv3.enums import TimePeriod


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


def _strip(text: str) -> str:
    return text.strip('"').strip("\n")


def _get_or_create_models(fields):
    theme, _ = Theme.objects.get_or_create(name=_strip(fields[0]))
    sub_theme, _ = SubTheme.objects.get_or_create(name=_strip(fields[1]), theme=theme)
    topic, _ = Topic.objects.get_or_create(
        name=_strip(fields[2]),
        sub_theme=sub_theme,
    )

    geography_type, _ = GeographyType.objects.get_or_create(name=_strip(fields[3]))
    geography, _ = Geography.objects.get_or_create(
        name=_strip(fields[4]),
        geography_type=geography_type,
    )

    metric, _ = Metric.objects.get_or_create(name=_strip(fields[5]), topic=topic)
    stratum, _ = Stratum.objects.get_or_create(name=_strip(fields[6]))

    metric_value = _strip(fields[10])
    if "NA" in metric_value:
        metric_value = "0"

    new_time_series = TimeSeries(
        epiweek=_strip(fields[8]),
        metric_value=metric_value,
        start_date=datetime.strptime(fields[9], "%Y-%m-%d"),
        year=_strip(fields[7]),
        period=TimePeriod.Weekly.value,
        metric=metric,
        stratum=stratum,
        geography=geography,
    )
    new_time_series.save()


def upload_data(data: io.TextIOWrapper) -> None:

    for index, line in enumerate(data, 0):

        fields: List[str] = line.split(",")
        if fields[0] != '"parent_theme"':
            try:
                _get_or_create_models(fields=fields)

            except ValueError:
                print(f"Error at line {index}")
