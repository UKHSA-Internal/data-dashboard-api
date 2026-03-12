from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.search import index
from wagtail.fields import RichTextField

from cms.error.managers import ErrorPageManager
from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
    UKHSAPage,
    UKHSAPageRelatedLink,
)
from cms.dynamic_content import help_texts
from cms.dynamic_content.announcements import Announcement


class ErrorPage(UKHSAPage):
    body = models.TextField(null=True, blank=True)
    error_line = models.TextField(
        help_text=help_texts.ERROR_PAGE_LINE_FIELD, blank=True, null=True)
    error_text = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.ERROR_PAGE_TEXT_FIELD,
    )
    sub_text = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.ERROR_PAGE_SUB_TEXT_FIELD,
    )
    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )

    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = UKHSAPage.content_panels + [
        FieldPanel("error_line"),
        FieldPanel("error_text"),
        FieldPanel("sub_text")
    ]

    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links",
                    label="Related link"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("error_line"),
        APIField("error_text"),
        APIField("sub_text"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("search_description"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.announcement_content_panels,
                       heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = ErrorPageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False


class ErrorPageRelatedLink(UKHSAPageRelatedLink):
    page = ParentalKey(
        ErrorPage, on_delete=models.SET_NULL, null=True, related_name="related_links"
    )


class ErrorPageAnnouncement(Announcement):
    page = ParentalKey(
        ErrorPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
