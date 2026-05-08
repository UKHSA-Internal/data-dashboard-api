import logging

from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    ObjectList,
    TabbedInterface,
    WagtailAdminPageForm,
)
from wagtail.api import APIField
from wagtail.search import index

from cms.auth_content.auth_utils import _create_form_field
from cms.dashboard.constants import THEME_FIELDS
from cms.dashboard.models import DataClassificationLevels, UKHSAPage
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_TEXT_SECTION
from cms.dynamic_content.announcements import Announcement
from cms.metrics_interface.field_choices_callables import (
    get_all_metric_names_and_ids,
)

logger = logging.getLogger(__name__)


class InvalidTopicForChosenMetricForChildEntryError(Exception):
    def __init__(self, topic: str, metric: str):
        message = f"The `{topic}` is not available for selected metric of `{metric}`"
        super().__init__(message)


class MetricsDocumentationChildEntryAdminForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in THEME_FIELDS:
            self.fields[field["field_name"]] = _create_form_field(field)

        if self.instance and self.instance.pk:
            self._initialize_dependent_fields()

    def _initialize_dependent_fields(self):
        """Initialize choices for cascading dependent fields"""
        dependent_fields = {
            "sub_theme": ("Select theme first"),
            "topic": ("Select sub-theme first"),
            # "metric": ("Select topic first"),
        }

        for field_name, (placeholder) in dependent_fields.items():
            value = getattr(self.instance, field_name, None)
            if value:
                choices = self._get_field_choices(value, placeholder)
                self.fields[field_name].widget.choices = choices

    @staticmethod
    def _get_field_choices(value, placeholder):
        """Generate choices list based on field value"""
        return [("", placeholder), (value, f"Loading... (ID: {value})")]

    class Media:
        js = ["js/toggle_available_fields_on_is_public.js"]


class MetricsDocumentationChildEntry(UKHSAPage):
    base_form_class = MetricsDocumentationChildEntryAdminForm
    page_description = models.TextField()
    metric = models.CharField(max_length=255)
    is_public = models.BooleanField(
        default=False,
        verbose_name="enable public page",
    )
    page_classification = models.CharField(
        max_length=50,
        choices=DataClassificationLevels.choices,
        default=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
        help_text=help_texts.PAGE_CLASSIFICATION,
        null=True,
        blank=True,
    )

    theme = models.CharField(max_length=255, blank=True, default="", null=True,)
    sub_theme = models.CharField(max_length=255, blank=True, default="", null=True,)
    topic = models.CharField(
        max_length=255,
        blank=True,
        default="",
        null=True
    )
    body = ALLOWABLE_BODY_CONTENT_TEXT_SECTION

    # Fields to index for searching within the CMS application.
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
    ]

    # Content panels to render for editing within the CMS application.
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("page_description"),
        FieldPanel("is_public"),
        FieldPanel("page_classification"),
        FieldPanel("theme"),
        FieldPanel("sub_theme"),
        FieldPanel("topic"),
        FieldPanel("metric"),
        FieldPanel("body"),
    ]

    # Sets which fields to expose on the API.
    api_fields = UKHSAPage.api_fields + [
        APIField("title"),
        APIField("metric"),
        APIField("topic"),
        APIField("metric_group"),
        APIField("is_public"),
        APIField("page_classification"),
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
        self._meta.get_field("metric").choices = get_all_metric_names_and_ids()

    def save(self, *args, **kwargs):
        """Retrieves a topic based on the selected metric

        Notes:
            This method will not be called when using `bulk_create()`
        """
        super().save(*args, **kwargs)

    @property
    def metric_group(self) -> str:
        field = self._meta.get_field("metric")
        choices = getattr(field, "choices", []) or []

        display_name = next((item[1] for item in choices if item[0] == self.metric), None)

        if not display_name or "_" not in display_name:
            return ""

        parts = display_name.split("_")
        return parts[1] if len(parts) > 1 else ""

    def clean(self):
        super().clean()

        # If is_public is true, automatically clear classification
        if self.is_public:
            self.page_classification = None
            self.theme = None
            self.sub_theme = None
            self.topic = None
            
        # If not public page, non-public fields must be set
        elif not self.page_classification:
            raise ValidationError(
                {
                    "page_classification": "Please select a classification level for this non-public page"
                }
            )
        elif not self.theme:
            raise ValidationError(
                {
                    "theme": "Please select a theme for this non-public page"
                }
            )
        elif not self.sub_theme:
            raise ValidationError(
                {
                    "sub_theme": "Please select a subtheme for this non-public page"
                }
            )
        elif not self.topic:
            raise ValidationError(
                {
                    "topic": "Please select a topic for this non-public page"
                }
            )


class MetricsDocumentationChildPageAnnouncement(Announcement):
    page = ParentalKey(
        MetricsDocumentationChildEntry,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
