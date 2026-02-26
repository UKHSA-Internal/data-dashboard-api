import logging

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.search import index

from cms.dashboard.models import UKHSAPage
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_TEXT_SECTION
from cms.dynamic_content.announcements import Announcement
from cms.metrics_interface.field_choices_callables import (
    get_a_list_of_all_topic_names,
    get_all_unique_metric_names,
)

logger = logging.getLogger(__name__)


class InvalidTopicForChosenMetricForChildEntryError(Exception):
    def __init__(self, topic: str, metric: str):
        message = f"The `{topic}` is not available for selected metric of `{metric}`"
        super().__init__(message)


class MetricsDocumentationChildEntry(UKHSAPage):
    page_description = models.TextField()
    metric = models.CharField(max_length=255)
    is_public = models.BooleanField(
        default=False,
        verbose_name="enable public page",
    )
    topic = models.CharField(
        max_length=255,
        default="",
    )
    body = ALLOWABLE_BODY_CONTENT_TEXT_SECTION

    # Fields to index for searching within the CMS application.
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("metric"),
        index.SearchField("body"),
    ]

    # Content panels to render for editing within the CMS application.
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("page_description"),
        FieldPanel("metric"),
        FieldPanel("is_public"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API.
    api_fields = UKHSAPage.api_fields + [
        APIField("title"),
        APIField("metric"),
        APIField("topic"),
        APIField("metric_group"),
        APIField("is_public"),
        APIField("body"),
        APIField("search_description"),
        APIField("last_published_at"),
        APIField("page_description"),
    ]

    # Tabs to position at the top of the view.
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(UKHSAPage.announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    parent_page_type = ["metrics_documentation.MetricsDocumentationParentPage"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["metric"],
                name="There can only be 1 `MetricsDocumentationChildEntry` for each `metric`",
            )
        ]

    def __init__(self, *args, **kwargs):
        """
        To dynamically load metric names into a choices field without
        using a foreign key relationship we first initialise an empty
        field on the model and then execute the following method to
        load in the names dynamically from the metrics interface.
        """
        super().__init__(*args, **kwargs)
        self._meta.get_field("metric").choices = get_all_unique_metric_names()

    def find_topic(self, *, topics: list[str]) -> str:
        """Finds the required topic from a list of strings based on the metric name.

        Args:
            topics: list of strings representing topic names.

        Returns:
            A string of the topic checked against the models metric value.

        Raises:
            `InvalidTopicForChosenMetricForChildEntry`: If the
                selected metric cannot be matched to a `Topic`

        """
        extracted_topic = self.metric.split("_")[0].lower()
        try:
            return next(topic for topic in topics if extracted_topic == topic.lower())
        except StopIteration as error:
            logger.info(
                "StopIteration Error: extracted topic not present in the topics list. %s",
                extracted_topic,
            )
            raise InvalidTopicForChosenMetricForChildEntryError(
                topic=extracted_topic, metric=self.metric
            ) from error

    def get_topic(self) -> str:
        """Finds the required topic name based on the selected metric name.

        Returns:
            a topic name as a string
        """
        topics = get_a_list_of_all_topic_names()
        return self.find_topic(topics=topics)

    def save(self, *args, **kwargs):
        """Retrieves a topic based on the selected metric

        Notes:
            This method will not be called when using `bulk_create()`
        """
        self.topic = self.get_topic()
        super().save(*args, **kwargs)

    @property
    def metric_group(self) -> str:
        return self.metric.split("_")[1]


class MetricsDocumentationChildPageAnnouncement(Announcement):
    page = ParentalKey(
        MetricsDocumentationChildEntry,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
