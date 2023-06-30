from django.db import models
from django.utils import timezone

from metrics.data.managers.core_models.geography import GeographyManager
from metrics.data.managers.core_models.geography_type import GeographyTypeManager
from metrics.data.managers.core_models.metric import MetricManager
from metrics.data.managers.core_models.stratum import StratumManager
from metrics.data.managers.core_models.topic import TopicManager

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

    objects = TopicManager()


class GeographyType(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = GeographyTypeManager()


class Geography(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography_type = models.ForeignKey(
        to=GeographyType, on_delete=models.SET_NULL, null=True
    )

    objects = GeographyManager()


class Metric(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    rounding = models.CharField(max_length=100)
    topic = models.ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)

    objects = MetricManager()


class Stratum(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = StratumManager()


class Age(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
