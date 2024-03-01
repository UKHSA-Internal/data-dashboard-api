from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


class ButtonTypes(models.Choices):
    """Enum for button types"""

    DOWNLOAD = "DOWNLOAD"
    SUBMIT = "SUBMIT"


class Methods(models.Choices):
    """Enum for method choices"""

    POST = "POST"
    GET = "GET"


@register_snippet
class Button(models.Model):
    text = models.CharField(max_length=255)
    loading_text = models.CharField(max_length=255, blank=True)
    endpoint = models.CharField(max_length=255, blank=True)
    method = models.CharField(
        max_length=255,
        choices=Methods.choices,
        default=Methods.POST.value,
        blank=False,
    )
    button_type = models.CharField(
        max_length=10,
        choices=ButtonTypes.choices,
        default=ButtonTypes.DOWNLOAD.value,
        blank=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["text", "button_type"],
                name="text and button type combinations should be unique",
            )
        ]

    panels = [
        FieldPanel("text"),
        FieldPanel("loading_text"),
        FieldPanel("button_type"),
    ]

    api_fields = [
        APIField("text"),
        APIField("loading_text"),
        APIField("button_type"),
        APIField("endpoint"),
        APIField("method"),
    ]

    def __str__(self) -> str:
        return f"Text: {self.text} | Type: {self.button_type}"
