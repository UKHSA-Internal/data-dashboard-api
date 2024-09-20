from django.db import models
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.models import Page

from cms.dashboard.models import UKHSAPage
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_SECTION_LINK
from cms.landing_page.managers import LandingPageManager


class LandingPage(UKHSAPage):
    is_creatable = True
    max_count = 1
    sub_title = models.CharField(max_length=255)
    body = ALLOWABLE_BODY_CONTENT_SECTION_LINK

    content_panels = Page.content_panels + [FieldPanel("sub_title"), FieldPanel("body")]

    api_fields = [
        APIField("sub_title"),
        APIField("body"),
        APIField("last_published_at"),
        APIField("search_description"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = LandingPageManager()

    @classmethod
    def is_previewable(cls):
        """Returns False. This is a headline CMS, preview panel is not supported ."""
        return False
