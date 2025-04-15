from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, ObjectList, TabbedInterface
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

from cms.dashboard.models import AVAILABLE_RICH_TEXT_FEATURES, UKHSAPage
from cms.dynamic_content import help_texts
from cms.dynamic_content.access import ALLOWABLE_BODY_CONTENT_SECTION_LINK
from cms.home.managers import LandingPageManager
from cms.snippets.models.global_banner import BannerTypes


class LandingPage(UKHSAPage):
    is_creatable = True
    max_count = 1
    sub_title = models.CharField(max_length=255)
    body = ALLOWABLE_BODY_CONTENT_SECTION_LINK

    content_panels = Page.content_panels + [FieldPanel("sub_title"), FieldPanel("body")]

    announcement_content_panels = [
        InlinePanel("announcements", heading="Announcements", label="Announcement"),
    ]

    api_fields = UKHSAPage.api_fields + [
        APIField("title"),
        APIField("sub_title"),
        APIField("body"),
        APIField("search_description"),
        APIField("last_published_at"),
        APIField("announcements"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(announcement_content_panels, heading="Announcements"),
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


class LandingPageAnnouncement(Orderable):
    page = ParentalKey(
        LandingPage, on_delete=models.SET_NULL, null=True, related_name="announcements"
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
