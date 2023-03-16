from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList, InlinePanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES


class HomePage(Page):
    body = RichTextField(blank=True, features=AVAILABLE_RICH_TEXT_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    sidebar_content_panels = [
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("body"),
        APIField("related_links"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(Page.promote_panels, heading="Promote"),

        ]
    )


class HomePageRelatedLink(Orderable):
    page = ParentalKey(
        HomePage, on_delete=models.SET_NULL, null=True, related_name="related_links"
    )
    title = models.CharField(max_length=255)
    url = models.URLField(verbose_name="URL")
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
