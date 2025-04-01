import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.search import index

from cms.common.models import MAXIMUM_URL_FIELD_LENGTH
from cms.composite.managers import CompositePageManager
from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES, UKHSAPage
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_COMPOSITE
from cms.snippets.models.global_banner import BannerTypes


class CompositePage(UKHSAPage):
    body = ALLOWABLE_BODY_CONTENT_COMPOSITE
    page_description = RichTextField(
        features=[],
        blank=True,
        null=True,
    )
    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Sidebar.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )
    show_pagination = models.BooleanField(
        default=True,
        help_text=help_texts.SHOW_PAGINATION_FIELD,
    )
    pagination_size = models.IntegerField(
        default=10,
        help_text=help_texts.PAGINATION_SIZE_FIELD,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(5),
        ],
    )

    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = UKHSAPage.content_panels + [
        FieldPanel("body"),
        FieldPanel("page_description"),
        FieldPanel("show_pagination"),
        FieldPanel("pagination_size"),
    ]

    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements", label="Announcement"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("body"),
        APIField("related_links"),
        APIField("search_description"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("announcements"),
        APIField("page_description"),
        APIField("show_pagination"),
        APIField("pagination_size"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = CompositePageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False

    @property
    def last_updated_at(self) -> datetime.datetime:
        """Takes the most recent update of this page and any of its children

        Notes:
            When calculating this timestamp,
            this property considers the following:
                - The latest content change of this page
                - The latest released embargo across all children
                - The latest content change across all children

        Returns:
            datetime object representing the last updated on the page
                across all children as well.

        """
        timestamps = [self.last_published_at]

        child_pages = [page.specific for page in self.get_children()]
        timestamps += [child_page.last_updated_at for child_page in child_pages]

        timestamps = [timestamp for timestamp in timestamps if timestamp]
        return max(timestamps)


class CompositeRelatedLink(Orderable):
    page = ParentalKey(
        CompositePage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="related_links",
    )
    title = models.CharField(max_length=255)
    url = models.URLField(verbose_name="URL", max_length=MAXIMUM_URL_FIELD_LENGTH)
    body = RichTextField(features=[], blank=True)

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


class CompositePageAnnouncement(Orderable):
    page = ParentalKey(
        CompositePage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    title = models.CharField(
        max_length=255,
        blank=False,
        help_text=help_texts.ANNOUNCEMENT_BANNER_TITLE,
    )
    badge = models.ForeignKey(
        "whats_new.badge",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(
        max_length=255,
        features=AVAILABLE_RICH_TEXT_FEATURES,
        help_text=help_texts.ANNOUNCEMENT_BANNER_BODY,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=BannerTypes.choices,
        default=BannerTypes.INFORMATION.value,
        help_text=help_texts.ANNOUNCEMENT_BANNER_TYPE,
    )

    is_active = models.BooleanField(
        default=False,
        help_text=help_texts.ANNOUNCEMENT_BANNER_IS_ACTIVE,
    )

    # Sets which panels to show on the editing view
    panels = [
        FieldPanel("title"),
        FieldPanel("badge"),
        FieldPanel("body"),
        FieldPanel("banner_type"),
        FieldPanel("is_active"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("title"),
        APIField("badge"),
        APIField("body"),
        APIField("banner_type"),
        APIField("is_active"),
    ]
