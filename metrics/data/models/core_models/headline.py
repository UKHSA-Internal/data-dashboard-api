from django.db import models
from django.db.models import Q

from metrics.data.managers.core_models.headline import CoreHeadlineManager
from metrics.data.models.constants import (
    METRIC_VALUE_DECIMAL_PLACES,
    METRIC_VALUE_MAX_DIGITS,
)
from metrics.data.models.core_models import help_texts
from metrics.data.models.core_models.supporting import Age, Geography, Metric, Stratum


class CoreHeadline(models.Model):
    metric = models.ForeignKey(
        to=Metric,
        on_delete=models.SET_NULL,
        null=True,
        help_text=help_texts.METRIC_HEADLINE,
    )
    geography = models.ForeignKey(
        to=Geography,
        on_delete=models.SET_NULL,
        null=True,
        help_text=help_texts.GEOGRAPHY,
    )
    stratum = models.ForeignKey(
        to=Stratum,
        on_delete=models.SET_NULL,
        null=True,
        help_text=help_texts.STRATUM,
    )
    age = models.ForeignKey(
        to=Age,
        on_delete=models.SET_NULL,
        null=True,
        help_text=help_texts.AGE,
    )
    sex = models.CharField(
        max_length=3,
        help_text=help_texts.SEX,
    )

    refresh_date = models.DateTimeField(help_text=help_texts.REFRESH_DATE)
    embargo = models.DateTimeField(help_text=help_texts.EMBARGO, null=True)

    period_start = models.DateTimeField(help_text=help_texts.PERIOD_START)
    period_end = models.DateTimeField(help_text=help_texts.PERIOD_END)
    upper_confidence = models.DecimalField(
        max_digits=METRIC_VALUE_MAX_DIGITS,
        decimal_places=METRIC_VALUE_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    metric_value = models.DecimalField(
        max_digits=METRIC_VALUE_MAX_DIGITS,
        decimal_places=METRIC_VALUE_DECIMAL_PLACES,
    )
    lower_confidence = models.DecimalField(
        max_digits=METRIC_VALUE_MAX_DIGITS,
        decimal_places=METRIC_VALUE_DECIMAL_PLACES,
        null=True,
        blank=True,
    )
    force_write = models.BooleanField(default=False)

    is_public = models.BooleanField(default=True, null=False)

    objects = CoreHeadlineManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "metric",
                    "geography",
                    "stratum",
                    "age",
                    "sex",
                    "period_start",
                    "period_end",
                    "metric_value",
                    "embargo",
                ),
                name="The `CoreHeadline` record should be unique if `force_write` is False",
                condition=Q(force_write=False),
            )
        ]

    def __str__(self):
        return f"Core Headline Data for {self.refresh_date}, metric '{self.metric.name}', value: {self.metric_value}"
