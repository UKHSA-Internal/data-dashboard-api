from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Page

from cms.dashboard.enums import (
    DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
    RelatedLinksLayoutEnum,
)
from cms.dashboard.models import (
    AVAILABLE_RICH_TEXT_FEATURES,
    UKHSAPage,
    UKHSAPageRelatedLink,
)
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_SECTION_LINK
from cms.dynamic_content.announcements import Announcement
from cms.home.managers import LandingPageManager


class LandingPage(UKHSAPage):
    is_creatable = True
    max_count = 1
    sub_title = models.CharField(max_length=255, null=True, blank=True)
    page_description = RichTextField(
        features=AVAILABLE_RICH_TEXT_FEATURES,
        blank=True,
        null=True,
        help_text=help_texts.PAGE_DESCRIPTION_FIELD,
    )
    body = ALLOWABLE_BODY_CONTENT_SECTION_LINK

    related_links_layout = models.CharField(
        verbose_name="Layout",
        help_text=help_texts.RELATED_LINKS_LAYOUT_FIELD,
        default=RelatedLinksLayoutEnum.Footer.value,
        max_length=DEFAULT_RELATED_LINKS_LAYOUT_FIELD_LENGTH,
        choices=RelatedLinksLayoutEnum.choices(),
    )

    sidebar_content_panels = [
        FieldPanel("related_links_layout"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("sub_title"),
        FieldPanel("page_description"),
        FieldPanel("body"),
    ]

    api_fields = UKHSAPage.api_fields + [
        APIField("title"),
        APIField("sub_title"),
        APIField("page_description"),
        APIField("body"),
        APIField("related_links_layout"),
        APIField("related_links"),
        APIField("search_description"),
        APIField("last_published_at"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(sidebar_content_panels, heading="Related Links"),
            ObjectList(UKHSAPage.announcement_content_panels, heading="Announcements"),
            ObjectList(UKHSAPage.promote_panels, heading="Promote"),
        ]
    )

    objects = LandingPageManager()

    @classmethod
    def is_previewable(cls):
        """Returns False. This is a headline CMS, preview panel is not supported ."""
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
                    This is because the landing page is assumed
                    to be at the root of the visible page tree.

        """
        site_id, root_url, page_path = super().get_url_parts(request=request)
        page_path = ""
        return site_id, root_url, page_path


class LandingPageAnnouncement(Announcement):
    page = ParentalKey(
        LandingPage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )


class LandingPageRelatedLink(UKHSAPageRelatedLink):
    page = ParentalKey(
        LandingPage, on_delete=models.SET_NULL, null=True, related_name="related_links"
    )
