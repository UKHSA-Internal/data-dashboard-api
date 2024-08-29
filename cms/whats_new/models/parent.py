from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES, MAXIMUM_URL_FIELD_LENGTH
from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import UKHSAPage
from cms.dynamic_content import help_texts
from cms.whats_new.managers.parent import WhatsNewParentPageManager


class WhatsNewParentPage(UKHSAPage):
    date_posted = models.DateField(null=False)
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )

    # Fields to index for searching within the CMS application
    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    # Content panels to render for editing within the CMS application
    content_panels = Page.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("date_posted"),
        APIField("body"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("last_published_at"),
        APIField("search_description"),
    ]

    # Adds inline content panels to be added to the `edit_handler`
    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]
    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    subpage_types = ["whats_new.WhatsNewChildEntry", "common.CommonPage"]

    objects = WhatsNewParentPageManager()


class WhatsNewParentPageRelatedLink(Orderable):
    page = ParentalKey(
        WhatsNewParentPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="related_links",
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
