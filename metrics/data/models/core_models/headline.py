from django.db import models

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

    refresh_date = models.DateField(help_text=help_texts.REFRESH_DATE)
    period_start = models.DateField(help_text=help_texts.PERIOD_START)
    period_end = models.DateField(help_text=help_texts.PERIOD_END)

    metric_value = models.DecimalField(
        max_digits=11,
        decimal_places=1,
    )

    def __str__(self):
        return f"Core Headline Data for {self.refresh_date}, metric '{self.metric.name}', value: {self.metric_value}"
