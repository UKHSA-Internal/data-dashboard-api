from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.search import index

from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
    UKHSAPage,
)
from cms.dynamic_content import help_texts
from cms.metrics_documentation.managers.parent import (
    MetricsDocumentationParentPageManager,
)
from cms.snippets.models.global_banner import BannerTypes


class MetricsDocumentationSlugNotValidError(ValidationError):
    def __init__(self):
        message = "The `MetricsDocumentationParentPage` must have a slug of `metrics-documentation"
        super().__init__(message)


class MetricsDocumentationMultipleLivePagesError(ValidationError):
    def __init__(self):
        message = "There should only be 1 `MetricsDocumentationParentPage"
        super().__init__(message)


class MetricsDocumentationParentPage(UKHSAPage):
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

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements", label="Announcement"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("body"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("announcements"),
        APIField("show_pagination"),
        APIField("pagination_size"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(announcement_content_panels, heading="Announcements"),
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


class MetricsDocumentationParentPageAnnouncement(Orderable):
    page = ParentalKey(
        MetricsDocumentationParentPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    title = models.CharField(
        max_length=255,
        blank=False,
        help_text=help_texts.GLOBAL_BANNER_TITLE,
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
        help_text=help_texts.GLOBAL_BANNER_BODY,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=BannerTypes.choices,
        default=BannerTypes.INFORMATION.value,
        help_text=help_texts.GLOBAL_BANNER_TYPE,
    )

    is_active = models.BooleanField(
        default=False,
        help_text=help_texts.GLOBAL_BANNER_IS_ACTIVE,
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
