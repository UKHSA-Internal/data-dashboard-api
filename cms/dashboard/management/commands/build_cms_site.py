"""
Utility to build out the basic CMS pages so we don't have to do so manually.
Only intended for use during development
"""

import os

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from cms.dashboard.management.commands import build_cms_site_helpers
from cms.home.models import HomePage, UKHSARootPage
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

        # Deprecated: to be removed after migration to landing page version two.
        home_page_dashboard: HomePage = (
            build_cms_site_helpers.create_home_page_dashboard(parent_page=root_page)
        )
        build_cms_site_helpers.create_topic_page(
            name="covid_19", parent_page=home_page_dashboard
        )
        build_cms_site_helpers.create_topic_page(
            name="influenza", parent_page=home_page_dashboard
        )
        build_cms_site_helpers.create_topic_page(
            name="other_respiratory_viruses", parent_page=home_page_dashboard
        )
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
        whats_new_parent_page = build_cms_site_helpers.create_whats_new_parent_page(
            name="whats_new", parent_page=root_page
        )

        build_cms_site_helpers.create_bulk_downloads_page(
            name="bulk_downloads", parent_page=root_page
        )

        # Create access our data parent and child page
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

        build_cms_site_helpers.create_whats_new_child_entry(
            name="whats_new_soft_launch_of_the_ukhsa_data_dashboard",
            parent_page=whats_new_parent_page,
        )

        create_metrics_documentation_parent_page_and_child_entries()

        weather_health_alerts_page = build_cms_site_helpers.create_composite_page(
            name="weather_health_alerts", parent_page=root_page
        )
        build_cms_site_helpers.create_composite_page(
            name="heat_health_alerts", parent_page=weather_health_alerts_page
        )
        build_cms_site_helpers.create_composite_page(
            name="cold_health_alerts", parent_page=weather_health_alerts_page
        )

        # landing page version two
        build_cms_site_helpers.create_landing_page(parent_page=root_page)

        build_cms_site_helpers.create_menu_snippet()

    @staticmethod
    def _clear_cms() -> None:
        # Wipe the existing site, pages & badges
        Site.objects.all().delete()
        Badge.objects.all().delete()
        Page.objects.filter(pk__gte=2).delete()  # Wagtail welcome page and all others
