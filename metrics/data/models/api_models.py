from django.db import models
from django.db.models import Q

from metrics.data.managers.api_models.time_series import APITimeSeriesManager
from metrics.data.models.constants import (
    CHAR_COLUMN_MAX_CONSTRAINT,
    GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT,
    LARGE_CHAR_COLUMN_MAX_CONSTRAINT,
    METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT,
    SEX_MAX_CHAR_CONSTRAINT,
)
from metrics.data.models.core_models import help_texts


class APITimeSeries(models.Model):
    metric_frequency = models.CharField(max_length=METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT)

    age = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT, null=True)
    month = models.PositiveSmallIntegerField(null=True)
    geography_code = models.CharField(
        max_length=GEOGRAPHY_CODE_MAX_CHAR_CONSTRAINT, null=True
    )
    metric_group = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT, null=True)
    theme = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sub_theme = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    topic = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography_type = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    geography = models.CharField(max_length=LARGE_CHAR_COLUMN_MAX_CONSTRAINT)
    metric = models.CharField(max_length=LARGE_CHAR_COLUMN_MAX_CONSTRAINT)
    stratum = models.CharField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)
    sex = models.CharField(max_length=SEX_MAX_CHAR_CONSTRAINT, null=True)
    year = models.PositiveSmallIntegerField()
    epiweek = models.PositiveSmallIntegerField()

    refresh_date = models.DateTimeField(null=True)
    embargo = models.DateTimeField(null=True)
    in_reporting_delay_period = models.BooleanField(
        help_text=help_texts.IN_REPORTING_DELAY_PERIOD,
        default=False,
    )

    date = models.DateField()
    force_write = models.BooleanField(default=False)
    metric_value = models.FloatField(max_length=CHAR_COLUMN_MAX_CONSTRAINT)

    is_public = models.BooleanField(default=True, null=False)

    objects = APITimeSeriesManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "metric",
                    "topic",
                    "theme",
                    "sub_theme",
                    "geography",
                    "geography_type",
                    "geography_code",
                    "stratum",
                    "age",
                    "sex",
                    "year",
                    "month",
                    "epiweek",
                    "date",
                    "metric_value",
                    "in_reporting_delay_period",
                    "embargo",
                ),
                name="The `APITimeSeries` record should be unique if `force_write` is False",
                condition=Q(force_write=False),
            )
        ]
        indexes = [
            models.Index(
                fields=[
                    "theme",
                    "sub_theme",
                    "topic",
                    "geography_type",
                    "geography",
                    "metric",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.__class__.__name__} for {self.date}, "
            f"metric '{self.metric}', "
            f"stratum '{self.stratum}', "
            f"value: {self.metric_value}"
        )
