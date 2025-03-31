from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface, InlinePanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.search import index

from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
    UKHSAPage,
)
from cms.dynamic_content import help_texts
from cms.snippets.models.global_banner import BannerTypes
from cms.whats_new.managers.parent import WhatsNewParentPageManager


class WhatsNewParentPage(UKHSAPage):
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

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements",
                    label="Announcement"),
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
        APIField("announcements")
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    subpage_types = ["whats_new.WhatsNewChildEntry", "common.CommonPage"]

    objects = WhatsNewParentPageManager()


class WhatsNewParentPageAnnouncement(Orderable):
    page = ParentalKey(
        WhatsNewParentPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    title = models.CharField(
        max_length=255,
        blank=False,
        help_text=help_texts.GLOBAL_BANNER_TITLE,
    )
    badge = models.ForeignKey(
        "whats_new.badge",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(
        max_length=255,
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.GLOBAL_BANNER_BODY,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=BannerTypes.choices,
        default=BannerTypes.INFORMATION.value,
        help_text=help_texts.GLOBAL_BANNER_TYPE,
    )

    is_active = models.BooleanField(
        default=False,
        help_text=help_texts.GLOBAL_BANNER_IS_ACTIVE,
    )

    # Sets which panels to show on the editing view
    panels = [
        FieldPanel("title"),
        FieldPanel("badge"),
        FieldPanel("body"),
        FieldPanel("banner_type"),
        FieldPanel("is_active"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("title"),
        APIField("badge"),
        APIField("body"),
        APIField("banner_type"),
        APIField("is_active"),
    ]
