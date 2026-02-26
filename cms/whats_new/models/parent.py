from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.search import index

from cms.dashboard.models import (
    UKHSAPage,
)
from cms.dynamic_content import help_texts
from cms.dynamic_content.announcements import Announcement
from cms.whats_new.managers.parent import WhatsNewParentPageManager


class WhatsNewParentPage(UKHSAPage):
    custom_preview_enabled: bool = True

    date_posted = models.DateField(null=False)
    show_pagination = models.BooleanField(
        default=True,
        help_text=help_texts.SHOW_PAGINATION_FIELD,
    )
    pagination_size = models.IntegerField(
        default=10,
        help_text=help_texts.PAGINATION_SIZE_FIELD,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(5),
        ],
    )

    # Fields to index for searching within the CMS application
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
    ]

    # Content panels to render for editing within the CMS application
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("body"),
        FieldPanel("show_pagination"),
        FieldPanel("pagination_size"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("date_posted"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("show_pagination"),
        APIField("pagination_size"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(UKHSAPage.announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    subpage_types = ["whats_new.WhatsNewChildEntry", "common.CommonPage"]

    objects = WhatsNewParentPageManager()


class WhatsNewParentPageAnnouncement(Announcement):
    page = ParentalKey(
        WhatsNewParentPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
