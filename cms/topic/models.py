import datetime

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface, WagtailAdminPageForm
from wagtail.api import APIField
from wagtail.fields import RichTextField, ValidationError
from wagtail.models import Orderable
from wagtail.search import index

from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
    MAXIMUM_URL_FIELD_LENGTH,
    UKHSAPage,
)
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT
from cms.dynamic_content.announcements import Announcement
from cms.dynamic_content.blocks_deconstruction import CMSBlockParser
from cms.metrics_interface import MetricsAPIInterface
from cms.topic.managers import TopicPageManager

DEFAULT_CORE_TIME_SERIES_MANGER = MetricsAPIInterface().core_time_series_manager
DEFAULT_CORE_HEADLINE_MANGER = MetricsAPIInterface().core_headline_manager


class DataClassificationLevels(models.TextChoices):
    OFFICIAL = "ABCDEFG"
    OFFICIAL_SENSITIVE = "official_sensitive"
    PM_NOT_SET = "protective_marking_not_set'"
    SECRET = "secret"  # noqa
    TOP_SECRET = "top_secret"  # noqa
    
class TopicPageAdminForm(WagtailAdminPageForm):
    class Media:
        js = ["topic/js/classification_toggle.js"]


class TopicPage(UKHSAPage):
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD,
    )
    body = ALLOWABLE_BODY_CONTENT

    enable_area_selector = models.BooleanField(default=False)

    is_public = models.BooleanField(
        default=False,
        verbose_name="enable public page",
    )

    page_classification = models.CharField(
        max_length=50,
        choices=DataClassificationLevels.choices,
        default=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
        help_text=help_texts.PAGE_CLASSIFICATION,
        blank = True,
        null = True
    )

    class Media:
        js = ['topic/js/disable_page_classification.js']
        css = ['topic/css/disable_page_classification.css']

    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )

    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Search index configuration
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("title"),
    ]

    # Editor panels configuration
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("enable_area_selector"),
        FieldPanel("is_public"),
        FieldPanel("page_classification"),
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("page_description"),
        APIField("body"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("enable_area_selector"),
        APIField("is_public"),
        APIField("page_classification"),
        APIField("selected_topics"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = TopicPageManager()

    def __init__(self, *args, **kwargs):
        core_timeseries_manager = kwargs.pop(
            "core_timeseries_manager", DEFAULT_CORE_TIME_SERIES_MANGER
        )
        core_headline_manager = kwargs.pop(
            "core_headline_manager", DEFAULT_CORE_HEADLINE_MANGER
        )
        super().__init__(*args, **kwargs)
        self._core_timeseries_manager = core_timeseries_manager
        self._core_headline_manager = core_headline_manager

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
    def selected_metrics(self) -> set[str]:
        """Extracts a set of the selected metrics from all the headline & chart blocks in the `body`

        Returns:
            Set of strings where each string represents
            a metric which has been selected at least
            once in the body of the page

        """
        return CMSBlockParser.get_all_selected_metrics_from_sections(
            sections=self.body.raw_data
        )

    def find_latest_released_embargo_for_metrics(
        self,
    ) -> list[datetime.datetime | None]:
        """Finds the latest `embargo` timestamp which has been released for the selected `metrics` on this page.

        Returns:
            A list of datetime object representing the latest
            released embargo timestamp
            for all time series and headline data on the page

        """
        selected_metrics = self.selected_metrics
        released_embargo_for_timeseries = (
            self._core_timeseries_manager.find_latest_released_embargo_for_metrics(
                metrics=selected_metrics
            )
        )
        released_embargo_for_headline = (
            self._core_headline_manager.find_latest_released_embargo_for_metrics(
                metrics=selected_metrics
            )
        )
        return [released_embargo_for_timeseries, released_embargo_for_headline]

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
        return self.enable_area_selector and len(self.selected_topics) == 1

    @property
    def is_page_public_selector(self) -> bool:
        """Determines whether this `TopicPage` is viewable to the public

        Returns:
            True if this `TopicPage` can be viewed by the public

        """
        return self.is_public

    @property
    def last_updated_at(self) -> datetime.datetime:
        """Fetches the time for the last content update or data update on the page.

        Returns:
            datetime object representing the last updated on the page

        """
        timestamps: list[datetime.datetime | None] = (
            self.find_latest_released_embargo_for_metrics()
        )
        timestamps.append(self.last_published_at)
        timestamps = [timestamp for timestamp in timestamps if timestamp]
        return max(timestamps)

    

    def clean(self):
        super().clean()

        # If is_public is true, automatically clear classification
        if self.is_public:
            self.page_classification = None
        else:
            # If not public, classification must be chosen
            if not self.page_classification:
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    "page_classification": "Please select a classification level for this non-public page"
                })



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


class TopicPageAnnouncement(Announcement):
    page = ParentalKey(
        TopicPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
