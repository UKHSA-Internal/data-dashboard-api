from django.db import models
from django.db.models import Q

from metrics.data.enums import TimePeriod
from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager
from metrics.data.models.constants import (
    METRIC_FREQUENCY_MAX_CHAR_CONSTRAINT,
    METRIC_VALUE_DECIMAL_PLACES,
    METRIC_VALUE_MAX_DIGITS,
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

    refresh_date = models.DateTimeField(help_text=help_texts.REFRESH_DATE, null=True)
    embargo = models.DateTimeField(help_text=help_texts.EMBARGO, null=True)
    in_reporting_delay_period = models.BooleanField(
        help_text=help_texts.IN_REPORTING_DELAY_PERIOD,
        default=False,
    )

    date = models.DateField()
    metric_value = models.DecimalField(
        max_digits=METRIC_VALUE_MAX_DIGITS,
        decimal_places=METRIC_VALUE_DECIMAL_PLACES,
    )
    force_write = models.BooleanField(default=False)

    is_public = models.BooleanField(default=True, null=False)

    objects = CoreTimeSeriesManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "metric",
                    "geography",
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
                name="The `CoreTimeSeries` record should be unique if `force_write` is False",
                condition=Q(force_write=False),
            )
        ]

    def __str__(self):
        return f"Core Timeseries Data for {self.date}, metric '{self.metric.name}', value: {self.metric_value}"
