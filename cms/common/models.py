from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from cms.common.managers import CommonPageManager
from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import UKHSAPage
from cms.dynamic_content import help_texts

HEADING_2: str = "h2"
HEADING_3: str = "h3"
HEADING_4: str = "h4"
BOLD: str = "bold"
BULLET_POINTS: str = "ul"
LINKS: str = "link"

AVAILABLE_RICH_TEXT_FEATURES: list[str] = [
    HEADING_2,
    HEADING_3,
    HEADING_4,
    BOLD,
    BULLET_POINTS,
    LINKS,
]


MAXIMUM_URL_FIELD_LENGTH: int = 400


class CommonPage(UKHSAPage):
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("body"),
        APIField("last_published_at"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("search_description"),
        APIField("related_links"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = CommonPageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False


class CommonPageRelatedLink(Orderable):
    page = ParentalKey(
        CommonPage, on_delete=models.SET_NULL, null=True, related_name="related_links"
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
