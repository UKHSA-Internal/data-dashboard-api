from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES, MAXIMUM_URL_FIELD_LENGTH
from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import UKHSAPage
from cms.dynamic_content import help_texts
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
    date_posted = models.DateField(null=False)
    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
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

    # Fields to index for searching within the CMS application
    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel("date_posted"),
        FieldPanel("body"),
        FieldPanel("show_pagination"),
        FieldPanel("pagination_size"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("date_posted"),
        APIField("body"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("last_published_at"),
        APIField("search_description"),
        APIField("show_pagination"),
        APIField("pagination_size"),
    ]

    # Adds inline content panels to be added to the `edit_handler`
    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
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


class MetricsDocumentationParentPageRelatedLinks(Orderable):
    page = ParentalKey(
        MetricsDocumentationParentPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="related_links",
    )
    title = models.CharField(max_length=255)
    url = models.URLField(verbose_name="URL", max_length=MAXIMUM_URL_FIELD_LENGTH)
    body = RichTextField(features=[])

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
