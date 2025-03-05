from django.db import models
from django.utils import timezone

from metrics.data.managers.core_models.age import AgeManager
from metrics.data.managers.core_models.geography import GeographyManager
from metrics.data.managers.core_models.geography_type import GeographyTypeManager
from metrics.data.managers.core_models.metric import MetricManager
from metrics.data.managers.core_models.stratum import StratumManager
from metrics.data.managers.core_models.topic import TopicManager
from metrics.data.models.constants import (
    CHAR_COLUMN_MAX_CONSTRAINT,
    GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT,
    LARGE_CHAR_COLUMN_MAX_CONSTRAINT,
)


class Theme(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    created_dt = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="`Theme` name should be unique"
            )
        ]

    def __str__(self):
        return self.name


class SubTheme(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    theme = models.ForeignKey(to=Theme, on_delete=models.SET_NULL, null=True)
    created_dt = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "theme"],
                name="`SubTheme` and `Theme` should be a unique combination",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.theme.name})"


class Topic(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sub_theme = models.ForeignKey(to=SubTheme, on_delete=models.SET_NULL, null=True)

    objects = TopicManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "sub_theme"],
                name="`Topic` and `SubTheme` should be a unique combination",
            )
        ]

    def __str__(self):
        return self.name


class MetricGroup(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    topic = models.ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("name", "topic"),
                name="`MetricGroup` and `Topic` should be a unique combination",
            ),
        ]


class Metric(models.Model):
    name = models.CharField(max_length=LARGE_CHAR_COLUMN_MAX_CONSTRAINT)

    topic = models.ForeignKey(to=Topic, on_delete=models.SET_NULL, null=True)
    metric_group = models.ForeignKey(
        to=MetricGroup, on_delete=models.SET_NULL, null=True
    )

    objects = MetricManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="`Metric` name should be unique"
            ),
            models.UniqueConstraint(
                fields=["name", "topic"],
                name="`Metric` and `Topic` should be a unique combination",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class GeographyType(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = GeographyTypeManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="`GeographyType` name should be unique"
            )
        ]

    def __str__(self):
        return self.name


class Geography(models.Model):
    name = models.CharField(max_length=LARGE_CHAR_COLUMN_MAX_CONSTRAINT)
    geography_code = models.CharField(
        max_length=GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT, null=True
    )
    geography_type = models.ForeignKey(
        to=GeographyType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="geographies",
    )

    objects = GeographyManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "geography_type"],
                name="`Geography` and `GeographyType` should be a unique combination",
            )
        ]

    def __str__(self):
        return self.name


class Stratum(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = StratumManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="`Stratum` name should be unique"
            )
        ]

    def __str__(self):
        return self.name


class Age(models.Model):
    name = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    objects = AgeManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name"], name="`Age` name should be unique")
        ]

    def __str__(self):
        return self.name
