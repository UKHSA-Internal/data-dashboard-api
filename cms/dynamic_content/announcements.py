from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable

from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
)
from cms.dynamic_content import help_texts
from cms.snippets.models.global_banner import BannerTypes


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
        APIField("is_active"),
    ]

    class Meta:
        abstract = True
