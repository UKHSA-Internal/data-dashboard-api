from django.db import models

from metrics.data.enums import TimePeriod
from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager
from metrics.data.models.constants import (
    METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT,
    SEX_MAX_CHAR_CONSTRAINT,
)
from metrics.data.models.core_models import help_texts
from metrics.data.models.core_models.supporting import Age, Geography, Metric, Stratum


class CoreTimeSeries(models.Model):
    metric = models.ForeignKey(
        to=Metric,
        on_delete=models.SET_NULL,
        null=True,
    )
    metric_frequency = models.CharField(
        max_length=METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT,
        choices=TimePeriod.choices(),
    )
    geography = models.ForeignKey(
        to=Geography,
        on_delete=models.SET_NULL,
        null=True,
    )
    stratum = models.ForeignKey(
        to=Stratum,
        on_delete=models.SET_NULL,
        null=True,
    )
    age = models.ForeignKey(
        to=Age,
        on_delete=models.SET_NULL,
        null=True,
        help_text=help_texts.AGE,
    )
    sex = models.CharField(
        max_length=SEX_MAX_CHAR_CONSTRAINT,
        null=True,
    )

    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField(null=True)
    epiweek = models.PositiveSmallIntegerField()

    date = models.DateField()
    refresh_date = models.DateField(help_text=help_texts.REFRESH_DATE, null=True)

    metric_value = models.DecimalField(
        max_digits=11,
        decimal_places=1,
    )

    objects = CoreTimeSeriesManager()

    def __str__(self):
        return f"Core Timeseries Data for {self.date}, metric '{self.metric.name}', value: {self.metric_value}"
