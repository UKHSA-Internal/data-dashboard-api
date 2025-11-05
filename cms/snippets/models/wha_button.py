from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


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

    panels = [
        FieldPanel("text"),
        FieldPanel("button_type"),
    ]

    api_fields = [
        APIField("text"),
        APIField("button_type"),
    ]

    def __str__(self) -> str:
        return f"Text: {self.text} | Type: {self.button_type}"
