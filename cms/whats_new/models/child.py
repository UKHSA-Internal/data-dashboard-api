from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface, InlinePanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.models import Orderable

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES, UKHSAPage
from cms.dynamic_content import help_texts
from cms.snippets.models.global_banner import BannerTypes
from cms.whats_new.managers.child import WhatsNewChildEntryManager
from cms.whats_new.serializers import BadgeSerializer


class WhatsNewChildEntry(UKHSAPage):
    date_posted = models.DateField(null=False, blank=False)
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
    )
    badge = models.ForeignKey(
        "whats_new.badge",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    additional_details = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES, null=True, blank=True
    )

    # Fields to index for searching within the CMS application
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
        index.SearchField("badge"),
    ]

    # Content panels to render for editing within the CMS application
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("page_description"),
        FieldPanel("body"),
        FieldPanel("additional_details"),
        FieldPanel("badge"),
    ]

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements",
                    label="Announcement"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("date_posted"),
        APIField("page_description"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("additional_details"),
        APIField("badge", serializer=BadgeSerializer()),
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

    parent_page_type = ["whats_new.WhatsNewParentPage"]

    objects = WhatsNewChildEntryManager()


class WhatsNewChildEntryAnnouncement(Orderable):
    page = ParentalKey(
        WhatsNewChildEntry,
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
