from typing import List

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

HEADING_2: str = "h2"
HEADING_3: str = "h3"
HEADING_4: str = "h4"
BOLD: str = "bold"
BULLET_POINTS: str = "ul"
LINKS: str = "link"

AVAILABLE_RICH_TEXT_FEATURES: List[str] = [
    HEADING_2,
    HEADING_3,
    HEADING_4,
    BOLD,
    BULLET_POINTS,
    LINKS,
]


class CommonPage(Page):
    date_posted = models.DateField()
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("body"),
    ]

    sidebar_content_panels = [
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("date_posted"),
        APIField("body"),
        APIField("last_published_at"),
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


class CommonPageRelatedLink(Orderable):
    page = ParentalKey(
        CommonPage, on_delete=models.SET_NULL, null=True, related_name="related_links"
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
