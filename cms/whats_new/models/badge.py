from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet

from cms.whats_new.colour_scheme import BadgeColours


@register_snippet
class Badge(models.Model):
    text = models.CharField(max_length=255)
    colour = models.CharField(
        max_length=20,
        choices=BadgeColours.choices,
        default=BadgeColours.GREY,
        blank=False,
    )

    # Sets which fields to expose on the CMS application to edit
    panels = [
        FieldPanel("text"),
        FieldPanel("colour"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("text"),
        APIField("colour"),
    ]

    def __str__(self) -> str:
        return f"Text: {self.text} | Colour: {self.colour}"
