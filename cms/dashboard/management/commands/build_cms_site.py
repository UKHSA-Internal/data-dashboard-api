"""
Utility to build out the basic CMS pages so we don't have to do so manually.
Only intended for use during development
"""

import os

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from cms.dashboard.management.commands import build_cms_site_helpers
from cms.home.models import UKHSARootPage
from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page_and_child_entries,
)
from cms.whats_new.models import Badge
from metrics.api.settings import WAGTAIL_SITE_NAME


def make_slug(*, page_title: str) -> str:
    """
    Make a CMS Slug from the page title

    Args:
        The page title (taken from the HTML Title Tag for the page)

    Returns:
        The page title as a slug with invalid characters removed.
        Currently only removes quotes, commas and full-stops.
    """
    return page_title.lower().replace("'", "").replace(" ", "-")


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Wipe the existing CMS pages and load in new ones
        """

        self._clear_cms()

        # Make a new home page
        title = "UKHSA Dashboard Root"
        slug = make_slug(page_title=title)
        root_page = UKHSARootPage(title=title, slug=slug)

        # Add this new home page onto the root
        wagtail_root_page = Page.get_first_root_node()
        wagtail_root_page.add_child(instance=root_page)
        wagtail_root_page.save_revision().publish()

        Site.objects.create(
            hostname=os.environ.get("FRONTEND_URL", "localhost"),
            port=443,
            site_name=WAGTAIL_SITE_NAME,
            root_page=root_page,
            is_default_site=True,
        )

        self._build_common_pages(root_page=root_page)

        self._build_access_our_data_section(root_page=root_page)
        self._build_whats_new_section(root_page=root_page)

        create_metrics_documentation_parent_page_and_child_entries()

        self._build_weather_health_alerts_section(root_page=root_page)
        self._build_respiratory_viruses_section(root_page=root_page)
        self._build_cover_section(root_page=root_page)

        build_cms_site_helpers.create_landing_page(parent_page=root_page)

        build_cms_site_helpers.create_acknowledgement_page(
            name="acknowledgement", parent_page=root_page
        )
        build_cms_site_helpers.create_feedback_page(
            name="feedback", parent_page=root_page
        )
        build_cms_site_helpers.create_menu_snippet()

    @classmethod
    def _build_whats_new_section(cls, root_page: UKHSARootPage) -> None:
        whats_new_parent_page = build_cms_site_helpers.create_whats_new_parent_page(
            name="whats_new", parent_page=root_page
        )
        build_cms_site_helpers.create_whats_new_child_entry(
            name="whats_new_soft_launch_of_the_ukhsa_data_dashboard",
            parent_page=whats_new_parent_page,
        )

    @classmethod
    def _build_weather_health_alerts_section(cls, root_page: UKHSARootPage) -> None:
        weather_health_alerts_page = build_cms_site_helpers.create_composite_page(
            name="weather_health_alerts", parent_page=root_page
        )
        build_cms_site_helpers.create_composite_page(
            name="heat_health_alerts", parent_page=weather_health_alerts_page
        )
        build_cms_site_helpers.create_composite_page(
            name="cold_health_alerts", parent_page=weather_health_alerts_page
        )

    @classmethod
    def _build_access_our_data_section(cls, root_page: UKHSARootPage) -> None:
        access_our_data_parent_page = build_cms_site_helpers.create_composite_page(
            name="access_our_data_parent_page", parent_page=root_page
        )
        build_cms_site_helpers.create_composite_page(
            name="access_our_data_getting_started",
            parent_page=access_our_data_parent_page,
        )
        build_cms_site_helpers.create_composite_page(
            name="access_our_data_data_structure",
            parent_page=access_our_data_parent_page,
        )
        build_cms_site_helpers.create_bulk_downloads_page(
            name="bulk_downloads", parent_page=root_page
        )

    @classmethod
    def _build_respiratory_viruses_section(cls, root_page: UKHSARootPage) -> None:
        covid_19_page = build_cms_site_helpers.create_topic_page(
            name="covid_19", parent_page=root_page
        )
        influenza_page = build_cms_site_helpers.create_topic_page(
            name="influenza", parent_page=root_page
        )
        other_respiratory_viruses_page = build_cms_site_helpers.create_topic_page(
            name="other_respiratory_viruses", parent_page=root_page
        )
        # Because the index page links to these pages
        # they need to be created first, referenced and then moved under the index page

        respiratory_viruses_index_page = (
            build_cms_site_helpers.create_respiratory_viruses_index_page(
                name="respiratory-viruses", parent_page=root_page
            )
        )

        other_respiratory_viruses_page.move(
            target=respiratory_viruses_index_page, pos="last-child"
        )
        influenza_page.move(target=respiratory_viruses_index_page, pos="last-child")
        covid_19_page.move(target=respiratory_viruses_index_page, pos="last-child")

    @classmethod
    def _build_cover_section(cls, root_page: UKHSARootPage) -> None:
        childhood_vaccinations_page = build_cms_site_helpers.create_topic_page(
            name="childhood_vaccinations", parent_page=root_page
        )

        # Because the index page links to these pages
        # they need to be created first, referenced and then moved under the index page
        cover_index_page = build_cms_site_helpers.create_cover_index_page(
            name="childhood_vaccinations_index", parent_page=root_page
        )

        childhood_vaccinations_page.move(target=cover_index_page, pos="last-child")

    @classmethod
    def _build_common_pages(cls, root_page: UKHSARootPage) -> None:
        build_cms_site_helpers.create_common_page(name="about", parent_page=root_page)
        build_cms_site_helpers.create_common_page(
            name="location_based_data", parent_page=root_page
        )
        build_cms_site_helpers.create_common_page(
            name="whats_coming", parent_page=root_page
        )
        build_cms_site_helpers.create_common_page(name="cookies", parent_page=root_page)
        build_cms_site_helpers.create_common_page(
            name="accessibility_statement", parent_page=root_page
        )
        build_cms_site_helpers.create_common_page(
            name="compliance", parent_page=root_page
        )

    @staticmethod
    def _clear_cms() -> None:
        # Wipe the existing site, pages & badges
        Site.objects.all().delete()
        Badge.objects.all().delete()
        Page.objects.filter(pk__gte=2).delete()  # Wagtail welcome page and all others
