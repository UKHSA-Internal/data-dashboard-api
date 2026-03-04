import datetime
from decimal import Decimal
from typing import override

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.templatetags.rest_framework import render_markdown
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Page, SiteRootPath

from cms import seo

HEADING_2: str = "h2"
HEADING_3: str = "h3"
HEADING_4: str = "h4"
BOLD: str = "bold"
BULLET_POINTS: str = "ul"
LINKS: str = "link"

AVAILABLE_RICH_TEXT_FEATURES: list[str] = [
    HEADING_2,
    HEADING_3,
    HEADING_4,
    BOLD,
    BULLET_POINTS,
    LINKS,
]

MAXIMUM_URL_FIELD_LENGTH: int = 400


class UKHSAPage(Page):
    """Abstract base class for all page types

    Notes:
        Since all page types extend from this class,
        be mindful of changes to fields here.
        As they will incur db migrations
        across multiple page types / tables.

    """

    custom_preview_enabled: bool = True

    body = RichTextField(features=AVAILABLE_RICH_TEXT_FEATURES)
    seo_change_frequency = models.IntegerField(
        verbose_name="SEO change frequency",
        help_text=render_markdown(markdown_text=seo.help_texts.SEO_CHANGE_FREQUENCY),
        default=seo.ChangeFrequency.Monthly,
        choices=seo.ChangeFrequency.choices,
    )
    seo_priority = models.DecimalField(
        verbose_name="SEO priority",
        help_text=seo.help_texts.SEO_PRIORITY,
        default=0.5,
        max_digits=2,
        decimal_places=1,
        validators=[
            MaxValueValidator(Decimal("1.0")),
            MinValueValidator(Decimal("0.1")),
        ],
    )

    api_fields = [
        APIField("body"),
        APIField("seo_change_frequency"),
        APIField("seo_title"),
        APIField("seo_priority"),
        APIField("last_updated_at"),
        APIField("last_published_at"),
        APIField("active_announcements"),
    ]

    promote_panels = [
        MultiFieldPanel(
            children=[
                FieldPanel("slug"),
                FieldPanel("seo_title"),
                FieldPanel("search_description"),
                FieldPanel("seo_change_frequency"),
                FieldPanel("seo_priority"),
            ],
            heading="For search engines",
        ),
    ]

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements", label="Announcement"),
    ]

    class Meta:
        abstract = True

    @override
    def is_previewable(self) -> bool:
        """Disable built-in Wagtail preview for all headless dashboard pages."""
        return False

    def _raise_error_if_slug_not_unique(self) -> None:
        """Compares the provided slug against all pages to confirm the slug's `uniqueness`
            this is against all pages and not just siblings, which is the default behavior of wagtail.

        Notes:
            The Data dashboard's front-end dynamically renders page's based on their slug, which means
            that validating this field only against siblings could lead to an issue if two or more pages
            share a slug even outside of the same parent-child relationship.
        """
        if Page.objects.live().filter(slug=self.slug).exclude(id=self.id).exists():
            raise ValidationError(
                {
                    "slug": "A page with this slug already exists. Please choose a unique slug."
                }
            )

    def _raise_error_if_seo_title_tag_not_provided(self) -> None:
        if not self.seo_title:
            raise ValidationError(message="Search engine title tag is required")

    def clean(self):
        super().clean()
        self._raise_error_if_slug_not_unique()
        self._raise_error_if_seo_title_tag_not_provided()

    def get_url_parts(self, request=None) -> tuple[int, str, str]:
        """Builds the full URL for this page

         Notes:
             Page url parts are returned as a tuple of
                (site_id, site_root_url, page_url_relative_to_site_root)
            The base implementation of this method assumes Wagtail
            is running in full app mode i.e not in headless,
            because the building of page paths is handed off to
            the `wagtail-serve` route which does not exist in headless mode.
            Hence, the need to override and provide the url here.

        Args:
            `request`: Optional request object which is not to
                be used for our implementation.

        Returns:
            Tuple containing the URL parts:
                1) ID of the corresponding `Site` record
                2) The root URL of the site
                    e.g. `https://ukhsa-dashboard.data.gov.uk`
                3) The path of the current page
                    e.g. `topics/covid-19`

        """
        possible_sites: tuple[SiteRootPath] = self._get_relevant_site_root_paths(
            request
        )
        site: SiteRootPath = possible_sites[0]

        root_path: str = site.root_path
        page_path = self.url_path.split(root_path)[1]
        page_path = f"/{page_path}"

        return site.site_id, site.root_url, page_path

    @property
    def last_updated_at(self) -> datetime.datetime:
        return self.last_published_at

    @property
    def active_announcements(self) -> list[dict[str, str | int]]:
        return list(
            self.announcements.filter(is_active=True)
            .order_by("-banner_type")
            .values("id", "title", "body", "banner_type")
        )
