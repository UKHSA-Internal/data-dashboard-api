from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

from cms.common.models import AVAILABLE_RICH_TEXT_FEATURES, MAXIMUM_URL_FIELD_LENGTH
from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import UKHSAPage
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT
from cms.home.managers import HomePageManager


class UKHSARootPage(Page):
    max_count = 1


class HomePage(UKHSAPage):
    max_count = 1
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD,
    )
    body = ALLOWABLE_BODY_CONTENT
    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )

    content_panels = Page.content_panels + [
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    # Sets which fields to expose on the API
    api_fields = UKHSAPage.api_fields + [
        APIField("page_description"),
        APIField("body"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("last_published_at"),
        APIField("search_description"),
    ]

    # Tabs to position at the top of the view
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = HomePageManager()

    @classmethod
    def is_previewable(cls) -> bool:
        """Returns False. Since this is a headless CMS the preview panel is not supported"""
        return False

    def get_url_parts(self, request=None) -> tuple[int, str, str]:
        """Builds the full URL for the home page

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
                3) The path of the current page.
                    This always returns an empty string
                    e.g. `""`
                    This is because the homepage is assumed
                    to be at the root of the visible page tree.

        """
        site_id, root_url, page_path = super().get_url_parts(request=request)
        page_path = ""
        return site_id, root_url, page_path


class HomePageRelatedLink(Orderable):
    page = ParentalKey(
        HomePage, on_delete=models.SET_NULL, null=True, related_name="related_links"
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
