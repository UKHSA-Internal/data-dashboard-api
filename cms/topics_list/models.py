from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.api import APIField
from wagtail.fields import RichTextField
from cms.dynamic_content import help_texts
from wagtail.search import index
from cms.dynamic_content.announcements import Announcement

from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_SECTION_LINK

from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
    UKHSAPage,
)
from cms.topics_list.managers import TopicsListPageManager


class TopicsListPage(UKHSAPage):
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD,
    )
    body = ALLOWABLE_BODY_CONTENT_SECTION_LINK

    objects = TopicsListPageManager()

    # Search index configuration
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("title"),
    ]

    # Editor panels
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("title"),
        APIField("page_description"),
        APIField("body"),
        APIField("last_published_at"),
        APIField("search_description"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading="Content"),
        ObjectList(UKHSAPage.announcement_content_panels, heading="Announcements"),
        ObjectList(UKHSAPage.promote_panels, heading="Promote"),
    ])

    @classmethod
    def is_previewable(cls):
        """Returns False. This is a headline CMS, preview panel is not supported ."""
        return False


class TopicsListPageAnnoucements(Announcement):
   page = ParentalKey(
       TopicsListPage,
       on_delete=models.SET_NULL,
       null=True,
       related_name="announcements",
   )
