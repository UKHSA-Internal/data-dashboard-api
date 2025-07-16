from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


class AccreditationBadgeTypes(models.Choices):
    Official = "Official"
    Official_Accredited = "Official Accredited"
    Experimental = "Experimental"


@register_snippet
class AccreditationBadge(models.Model):
    accreditation_type = models.CharField(
        max_length=25,
        choices=AccreditationBadgeTypes.choices,
        blank=False,
    )

    panels = [
        FieldPanel("accreditation_type"),
    ]

    api_fields = [
        APIField("accreditation_type"),
    ]

    def __str__(self) -> str:
        return f"Accreditation Type: {self.accreditation_type}"
