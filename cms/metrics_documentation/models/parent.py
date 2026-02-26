from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.search import index

from cms.dashboard.models import (
    UKHSAPage,
)
from cms.dynamic_content import help_texts
from cms.dynamic_content.announcements import Announcement
from cms.metrics_documentation.managers.parent import (
    MetricsDocumentationParentPageManager,
)


class MetricsDocumentationSlugNotValidError(ValidationError):
    def __init__(self):
        message = "The `MetricsDocumentationParentPage` must have a slug of `metrics-documentation"
        super().__init__(message)


class MetricsDocumentationMultipleLivePagesError(ValidationError):
    def __init__(self):
        message = "There should only be 1 `MetricsDocumentationParentPage"
        super().__init__(message)


class MetricsDocumentationParentPage(UKHSAPage):
    custom_preview_enabled: bool = True

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

    # Fields to index for searching within the CMS application
    search_fields = UKHSAPage.search_fields + [
        index.SearchField("body"),
    ]

    # Editor panels configuration
    content_panels = UKHSAPage.content_panels + [
        FieldPanel("body"),
        FieldPanel("show_pagination"),
        FieldPanel("pagination_size"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("body"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("show_pagination"),
        APIField("pagination_size"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(UKHSAPage.announcement_content_panels, "Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = MetricsDocumentationParentPageManager()

    subpage_types = [
        "metrics_documentation.MetricsDocumentationChildEntry",
        "common.CommonPage",
    ]

    def clean(self) -> None:
        super().clean()
        self._raise_error_if_slug_not_metrics_documentation()
        self._raise_error_for_multiple_live_pages()

    def _raise_error_if_slug_not_metrics_documentation(self) -> None:
        if "metrics-documentation" not in self.slug:
            raise MetricsDocumentationSlugNotValidError

    def _raise_error_for_multiple_live_pages(self) -> None:
        live_pages = MetricsDocumentationParentPage.objects.get_live_pages()
        if live_pages.count() == 1 and self.pk != live_pages[0].id:
            raise MetricsDocumentationMultipleLivePagesError


class MetricsDocumentationParentPageAnnouncement(Announcement):
    page = ParentalKey(
        MetricsDocumentationParentPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
