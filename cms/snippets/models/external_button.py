from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet

from cms.dynamic_content.help_texts import BUTTON_ICON, BUTTON_TYPE_GDS


class ExternalButtonTypes(models.TextChoices):
    PRIMARY = "Primary"
    SECONDARY = "Secondary"
    WARNING = "Warning"

    @classmethod
    def get_external_button_types(cls) -> tuple[tuple[str, str]]:
        return tuple((button_type.value, button_type.value) for button_type in cls)


class ExternalButtonIcons(models.TextChoices):
    EMPTY = "None"
    DOWNLOAD = "Download"
    START = "Start"

    @classmethod
    def get_external_button_icons(cls) -> tuple[tuple[str, str]]:
        return tuple((icon.value, icon.value) for icon in cls)


@register_snippet
class ExternalButton(models.Model):
    text = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    button_type = models.CharField(
        max_length=255,
        choices=ExternalButtonTypes.get_external_button_types,
        default=ExternalButtonTypes.PRIMARY.value,
        help_text=BUTTON_TYPE_GDS,
    )
    icon = models.CharField(
        max_length=255,
        choices=ExternalButtonIcons.get_external_button_icons,
        default=ExternalButtonIcons.EMPTY.value,
        help_text=BUTTON_ICON,
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
