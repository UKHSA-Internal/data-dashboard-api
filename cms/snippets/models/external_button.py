from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet

from cms.dynamic_content.help_texts import BUTTON_ICON, BUTTON_TYPE_GDS


class ExternalButtonTypes(models.TextChoices):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    WARNING = "Warning"


class ExternalButtonIcons(models.TextChoices):
    DOWNLOAD = "Download"
    START = "Start"


@register_snippet
class ExternalButton(models.Model):
    text = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    button_type = models.CharField(
        max_length=255,
        choices=ExternalButtonTypes.choices,
        default=ExternalButtonTypes.PRIMARY.value,
        help_text=BUTTON_TYPE_GDS,
    )
    icon = models.CharField(
        max_length=255,
        choices=ExternalButtonIcons.choices,
        help_text=BUTTON_ICON,
        blank=True,
    )

    panels = [
        FieldPanel("text"),
        FieldPanel("url"),
        FieldPanel("button_type"),
        FieldPanel("icon"),
    ]

    api_fields = [
        APIField("text"),
        APIField("url"),
        APIField("button_type"),
        APIField("icon"),
    ]

    def __str__(self) -> str:
        return f"Text: {self.text} | Type: {self.button_type}"
