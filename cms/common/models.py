from typing import List

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

HEADING_2: str = "h2"
HEADING_3: str = "h3"
BOLD: str = "bold"
BULLET_POINTS: str = "ul"
LINKS: str = "link"

AVAILABLE_RICH_TEXT_FEATURES: List[str] = [
    HEADING_2,
    HEADING_3,
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

    api_fields = [
        APIField("date_posted"),
        APIField("body"),
    ]
