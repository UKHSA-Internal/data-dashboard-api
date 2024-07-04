from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework.templatetags.rest_framework import render_markdown
from wagtail.admin.panels.field_panel import FieldPanel
from wagtail.api import APIField
from wagtail.models import Page, SiteRootPath

from cms import seo


class UKHSAPage(Page):
    """Abstract base class for all page types

    Notes:
        Since all page types extend from this class,
        be mindful of changes to fields here.
        As they will incur db migrations
        across multiple page types / tables.

    """

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
        APIField("seo_change_frequency"),
        APIField("seo_title"),
        APIField("seo_priority"),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("seo_change_frequency"),
        FieldPanel("seo_priority"),
    ]

    class Meta:
        abstract = True

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
        possible_sites: tuple[SiteRootPath] = self._get_relevant_site_root_paths(request)
        site: SiteRootPath = possible_sites[0]

        root_path: str = site.root_path
        page_path = self.url_path.split(root_path)[1]
        page_path = f"/{page_path}"

        return site.site_id, site.root_url, page_path
