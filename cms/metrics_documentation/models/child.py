import logging

from django.db import models
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.blocks import CharBlock, ChoiceBlock, RichTextBlock
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from cms.metrics_documentation.managers.child import MetricsDocumentationChildEntryManager
from cms.metrics_interface.field_choices_callables import (
    get_all_unique_metric_names,
    # get_all_topic_names,
)


class MetricsDocumentationChildEntry(Page):
    date_posted = models.DateField(null=False)
    page_description = models.TextField()
    metric_choices = get_all_unique_metric_names()
    metric_name = models.CharField(
        max_length=255,
        choices=metric_choices,
        default=metric_choices[0],
    )
    body = StreamField([
        ("title", CharBlock(help_text="section title", required=True)),
        ("content", RichTextBlock(help_text="section content", required=True)),
    ], use_json_field=True)

    # Fields to index for searching within the CMS application
    search_fields = Page.search_fields + [
        index.SearchField("metric_name"),
        index.SearchField("body"),
    ]

    # Content panels to render for editing within the CMS application
    content_panels = Page.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("metric_name"),
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API
    api_fields = [
        APIField("date_posted"),
        APIField("metric_name"),
        APIField("body"),
        APIField("search_description"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Promote"),
        ]
    )

    # Objects manager
    objects = MetricsDocumentationChildEntryManager()

    # def save(self, *args, **kwargs):
    #     topics = get_all_topic_names()
    #     self.topic = [topic for topic in topics if self.metric_name.split("_")[0] in topic[0].lower()]
    #     return super().save(*args, **kwargs)

    # @property
    # def metric_group(self):
    #     return self.metric_name.split("_")[1]
