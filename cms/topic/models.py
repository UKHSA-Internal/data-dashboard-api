from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES, MAXIMUM_URL_FIELD_LENGTH
from cms.dashboard.models import UKHSAPage
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT
from cms.dynamic_content.blocks_deconstruction import CMSBlockParser
from cms.topic.managers import TopicPageManager


class TopicPage(UKHSAPage):
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD,
    )
    body = ALLOWABLE_BODY_CONTENT
    date_posted = models.DateField()

    enable_area_selector = models.BooleanField(default=False)

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
        FieldPanel("enable_area_selector"),
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("page_description"),
        APIField("body"),
        APIField("related_links"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("enable_area_selector"),
        APIField("selected_topics"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = TopicPageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False

    @property
    def selected_topics(self) -> set[str]:
        """Extracts a set of the selected topics from all the headline & chart blocks in the `body`

        Returns:
            Set of strings where each string represents
            a topic which has been selected at least
            once in the body of the page

        """
        return CMSBlockParser.get_all_selected_topics_from_sections(
            sections=self.body.raw_data
        )

    @property
    def is_valid_for_area_selector(self) -> bool:
        """Determines whether this `TopicPage` is available and valid for the area selector

        Notes:
            The criteria for being valid for the area selector
            are as follows:
                1) The `enable_area_selector` field must be True
                2) The `selected_topics` field must have a length of 1

        Returns:
            True if this `TopicPage` can be processed
            by the area selector. False otherwise.

        """
        return len(self.selected_topics) == 1 and self.enable_area_selector


class TopicPageRelatedLink(Orderable):
    page = ParentalKey(
        TopicPage, on_delete=models.SET_NULL, null=True, related_name="related_links"
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
