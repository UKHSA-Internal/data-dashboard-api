from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES, MAXIMUM_URL_FIELD_LENGTH
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT
from cms.home.managers import HomePageManager


class HomePage(Page):
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD,
    )
    body = ALLOWABLE_BODY_CONTENT

    content_panels = Page.content_panels + [
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    sidebar_content_panels = [
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("page_description"),
        APIField("body"),
        APIField("related_links"),
        APIField("last_published_at"),
        APIField("seo_title"),
        APIField("search_description"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(Page.promote_panels, heading="Promote"),
        ]
    )

    objects = HomePageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False


class HomePageRelatedLink(Orderable):
    page = ParentalKey(
        HomePage, on_delete=models.SET_NULL, null=True, related_name="related_links"
    )
    title = models.CharField(max_length=255)
    url = models.URLField(verbose_name="URL", max_length=MAXIMUM_URL_FIELD_LENGTH)
    body = RichTextField(features=[])

    # Sets which panels to show on the editing view
    panels = [
        FieldPanel("title"),
        FieldPanel("url"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("title"),
        APIField("url"),
        APIField("body"),
    ]
