from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from cms.dynamic_content import help_texts

HEADING_2: str = "h2"
HEADING_3: str = "h3"
HEADING_4: str = "h4"
BOLD: str = "bold"
BULLET_POINTS: str = "ul"
LINKS: str = "link"

AVAILABLE_RICH_TEXT_FEATURES: list[str] = [
    HEADING_2,
    HEADING_3,
    HEADING_4,
    BOLD,
    BULLET_POINTS,
    LINKS,
]


class BannerTypes(models.TextChoices):
    INFORMATION = "Information"
    WARNING = "Warning"


class Announcement(Orderable):
    title = models.CharField(
        max_length=255,
        blank=False,
        help_text=help_texts.ANNOUNCEMENT_BANNER_TITLE,
    )
    body = RichTextField(
        max_length=255,
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.ANNOUNCEMENT_BANNER_BODY,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=BannerTypes.choices,
        default=BannerTypes.INFORMATION.value,
        help_text=help_texts.ANNOUNCEMENT_BANNER_TYPE,
    )

    is_active = models.BooleanField(
        default=False,
        help_text=help_texts.ANNOUNCEMENT_BANNER_IS_ACTIVE,
    )

    # Sets which panels to show on the editing view
    panels = [
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("banner_type"),
        FieldPanel("is_active"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("title"),
        APIField("body"),
        APIField("banner_type"),
    ]

    class Meta:
        abstract = True
