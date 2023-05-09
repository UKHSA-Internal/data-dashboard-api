from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT


class TopicPage(Page):
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD_HELP_TEXT,
    )
    body = ALLOWABLE_BODY_CONTENT
    date_posted = models.DateField()

    # TopicPage Bespoke content fields
    symptoms = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    transmission = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    treatment = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    prevention = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    surveillance_and_reporting = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)

    sidebar_content_panels = [
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Search index configuration
    search_fields = Page.search_fields + [
        index.SearchField("title"),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("page_description"),
        FieldPanel("body"),
        FieldPanel("symptoms"),
        FieldPanel("transmission"),
        FieldPanel("treatment"),
        FieldPanel("prevention"),
        FieldPanel("surveillance_and_reporting"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("body"),
        APIField("symptoms"),
        APIField("transmission"),
        APIField("treatment"),
        APIField("prevention"),
        APIField("surveillance_and_reporting"),
        APIField("related_links"),
        APIField("last_published_at"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(Page.promote_panels, heading="Promote"),
        ]
    )


class TopicPageRelatedLink(Orderable):
    page = ParentalKey(
        TopicPage, on_delete=models.SET_NULL, null=True, related_name="related_links"
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
