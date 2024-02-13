from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from cms.common.models import MAXIMUM_URL_FIELD_LENGTH
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_COMPOSITE


class CompositePage(Page):
    date_posted = models.DateField()
    body = ALLOWABLE_BODY_CONTENT_COMPOSITE

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("body"),
    ]

    sidebar_content_panels = [
        InlinePanel("related_links", heading="Related links", label="Related link")
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("date_posted"),
        APIField("body"),
        APIField("last_published_at"),
        APIField("related_links"),
        APIField("seo_title"),
        APIField("search_description"),
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

    def is_previewable(self) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False


class CompositeRelatedLink(Orderable):
    page = ParentalKey(
        CompositePage,
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
