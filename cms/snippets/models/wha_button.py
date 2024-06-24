from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet

from cms.metrics_interface.field_choices_callables import (
    get_all_geography_names_and_codes_for_alerts,
)


class WeatherAlertButtonTypes(models.Choices):
    """Enum for weather alert button type"""

    HEAT = "Heat"
    COLD = "Cold"


@register_snippet
class WeatherAlertButton(models.Model):
    text = models.CharField(max_length=255)
    button_type = models.CharField(
        max_length=25,
        choices=WeatherAlertButtonTypes.choices,
        default=WeatherAlertButtonTypes.HEAT.value,
        blank=False,
    )
    geography_code = models.CharField(
        max_length=9,
        choices=get_all_geography_names_and_codes_for_alerts,
        blank=True,
    )

    panels = [
        FieldPanel("text"),
        FieldPanel("button_type"),
        FieldPanel("geography_code"),
    ]

    api_fields = [
        APIField("text"),
        APIField("button_type"),
        APIField("geography_code"),
    ]

    def __str__(self) -> str:
        if not self.geography_code:
            return f"Text: {self.text} | Type: {self.button_type}"

        return f"Text: {self.text} | Type: {self.button_type} | {self.geography_code}"
