from django import forms
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.search import index

from cms.auth_content.forms.non_public_page import NonPublicPageAdminForm
from cms.auth_content.models.non_public_page import NonPublicCapablePage
from cms.dashboard.models import UKHSAPage
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_TEXT_SECTION
from cms.dynamic_content.announcements import Announcement
from cms.metrics_interface.field_choices_callables import get_all_unique_metric_names


class MetricsDocumentationChildEntryAdminForm(NonPublicPageAdminForm):
    """
    Admin form for child entries. All this does currently is populate the metric field's choices.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # the metric field's form has been initialised as just a simple char field with a select widget and no choices,
        # here we set the choices
        self.fields["metric"].widget.choices = [
            ("", "----------"),
            *get_all_unique_metric_names(),
        ]


class MetricsDocumentationChildEntry(UKHSAPage, NonPublicCapablePage):
    base_form_class = MetricsDocumentationChildEntryAdminForm

    page_description = models.TextField()
    metric = models.CharField(max_length=255)
    body = ALLOWABLE_BODY_CONTENT_TEXT_SECTION

    # Fields to index for searching within the CMS application.
    search_fields = [
        *UKHSAPage.search_fields,
        index.SearchField("body"),
        *NonPublicCapablePage.search_fields,
    ]

    # Content panels to render for editing within the CMS application.
    content_panels = UKHSAPage.content_panels + [
        *NonPublicCapablePage.content_panels,
        FieldPanel("page_description"),
        FieldPanel("metric", widget=forms.Select()),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API.
    api_fields = UKHSAPage.api_fields + [
        APIField("title"),
        APIField("metric"),
        APIField("body"),
        *NonPublicCapablePage.api_fields,
        APIField("search_description"),
        APIField("last_published_at"),
        APIField("page_description"),
        APIField("topic"),
        APIField("metric_group"),
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

    @property
    def topic(self) -> str:
        """
        API field `topic`, simply extract the topic from the metric name.
        """
        if not self.metric or "_" not in self.metric:
            return ""
        return self.metric.split("_")[0]

    @property
    def metric_group(self) -> str:
        """
        API field `metric_group`, simply extract the group from the metric name.
        """
        # the metric name isn't valid if it doesn't have at least 2 underscores in it
        minimum_valid_underscore_count = 2
        if not self.metric or self.metric.count("_") < minimum_valid_underscore_count:
            return ""
        return self.metric.split("_")[1]


class MetricsDocumentationChildPageAnnouncement(Announcement):
    page = ParentalKey(
        MetricsDocumentationChildEntry,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
