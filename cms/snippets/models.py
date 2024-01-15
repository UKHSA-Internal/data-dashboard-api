from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


class ButtonTypes(models.Choices):
    """Enum for button types"""

    DOWNLOAD = "DOWNLOAD"
    SUBMIT = "SUBMIT"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """ """
        return [(button_type, button_type) for button_type in cls]


def get_scores():
    return [(i, str(i)) for i in range(10)]


@register_snippet
class Button(models.Model):
    text = models.CharField(max_length=255)
    loading_text = models.CharField(max_length=255, blank=True)
    endpoint = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=255, default="POST", blank=False)
    button_type = models.CharField(max_length=35)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["text", "button_type"],
                name="text and button type combinations should be unique",
            )
        ]

    def __init__(self, *args, **kwargs):
        """ """
        super().__init__(*args, **kwargs)
        self._meta.get_field("button_type").choices = get_scores()

    panels = [
        FieldPanel("text"),
        FieldPanel("loading_text"),
        FieldPanel("button_type"),
    ]

    api_fields = [
        APIField("text"),
        APIField("loading_text"),
        APIField("link"),
        APIField("button_type"),
    ]

    def __str__(self) -> str:
        return f"Text: {self.text} | Type: {self.button_type}"
