"""
Utility to build out the basic CMS pages so we don't have to do so manually.
Only intended for use during development
"""

import json
import logging
import os

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from cms.common.models import CommonPage, CommonPageRelatedLink
from cms.composite.models import CompositePage, CompositeRelatedLink
from cms.home.models import HomePage, HomePageRelatedLink
from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page_and_child_entries,
)
from cms.snippets.data_migrations.operations import (
    get_or_create_download_button_internal_button_snippet,
)
from cms.topic.models import TopicPage, TopicPageRelatedLink
from cms.whats_new.models import Badge, WhatsNewChildEntry, WhatsNewParentPage
from cms.whats_new.models.parent import WhatsNewParentPageRelatedLink
from metrics.api.settings import ROOT_LEVEL_BASE_DIR, WAGTAIL_SITE_NAME

logger = logging.getLogger(__name__)

FILE_PATH = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/"


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


def open_example_page_response(*, page_name: str):
    path = f"{FILE_PATH}{page_name}.json"
    with open(path, "rb") as f:
        return json.load(f)


def _create_related_links(*, related_link_class, response_data, page) -> None:
    for related_link_response_data in response_data["related_links"]:
        related_link_model = related_link_class(
            page=page,
            title=related_link_response_data["title"],
            url=related_link_response_data["url"],
            body=related_link_response_data["body"],
        )
        related_link_model.save()


def _add_page_to_parent(*, page: Page, parent_page: HomePage) -> None:
    page = parent_page.add_child(instance=page)
    page.save_revision().publish()


def _create_landing_dashboard_page(*, parent_page: Page) -> HomePage:
    data = open_example_page_response(page_name="ukhsa_data_dashboard")

    page = HomePage(
        body=data["body"],
        title=data["title"],
        page_description=data["page_description"],
        slug=data["meta"]["slug"],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=HomePageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _create_topic_page(*, name: str, parent_page: Page) -> TopicPage:
    data = open_example_page_response(page_name=name)

    page = TopicPage(
        body=data["body"],
        title=data["title"],
        page_description=data["page_description"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=TopicPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _create_common_page(*, name: str, parent_page: Page) -> CommonPage:
    data = open_example_page_response(page_name=name)

    page = CommonPage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=CommonPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _remove_comment_from_body(*, body: dict[list[dict]]) -> list[dict]:
    return [item for item in body if "_comment" not in item]


def _get_or_create_button_id() -> int:
    internal_button_snippet = get_or_create_download_button_internal_button_snippet()
    return internal_button_snippet.id


def _add_download_button_to_composite_body(
    *, body: dict[list[dict]]
) -> dict[list[dict]]:
    body.append(
        {
            "type": "internal_button",
            "value": _get_or_create_button_id(),
            "id": "1431bc99-d4f9-4c80-880b-e96c5ad098db",
        }
    )
    return body


def _create_bulk_downloads_page(*, name: str, parent_page: Page) -> CompositePage:
    data = open_example_page_response(page_name=name)

    body = _remove_comment_from_body(body=data["body"])
    composite_body = _add_download_button_to_composite_body(body=body)

    page = CompositePage(
        body=composite_body,
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
    )

    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=CompositeRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _create_composite_page(*, name: str, parent_page: Page) -> CompositePage:
    data = open_example_page_response(page_name=name)

    page = CompositePage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
    )

    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=CompositeRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _create_whats_new_parent_page(
    *, name: str, parent_page: Page
) -> WhatsNewParentPage:
    data = open_example_page_response(page_name=name)

    page = WhatsNewParentPage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _create_related_links(
        related_link_class=WhatsNewParentPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _create_whats_new_child_entry(
    *, name: str, parent_page: Page
) -> WhatsNewChildEntry:
    data = open_example_page_response(page_name=name)

    badge = Badge(text=data["badge"]["text"], colour=data["badge"]["colour"])
    badge.save()

    entry = WhatsNewChildEntry(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        seo_title=data["meta"]["seo_title"],
        search_description=data["meta"]["search_description"],
        show_in_menus=data["meta"]["show_in_menus"],
        additional_details=data["additional_details"],
        badge=badge,
    )
    _add_page_to_parent(page=entry, parent_page=parent_page)

    return entry


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Wipe the existing CMS pages and load in new ones
        """

        self._clear_cms()

        # Make a new home page
        title = "UKHSA Dashboard Root"
        slug = make_slug(page_title=title)
        root_page = HomePage(title=title, slug=slug)

        # Add this new home page onto the root
        wagtail_root_page = Page.get_first_root_node()
        wagtail_root_page.add_child(instance=root_page)
        wagtail_root_page.save_revision().publish()

        Site.objects.create(
            hostname=os.environ.get("FRONTEND_URL", "localhost"),
            port=443,
            site_name=WAGTAIL_SITE_NAME,
            root_page=wagtail_root_page,
            is_default_site=True,
        )

        landing_dashboard_page: HomePage = _create_landing_dashboard_page(
            parent_page=root_page
        )
        _create_topic_page(name="covid_19", parent_page=landing_dashboard_page)
        _create_topic_page(name="influenza", parent_page=landing_dashboard_page)
        _create_topic_page(
            name="other_respiratory_viruses", parent_page=landing_dashboard_page
        )
        _create_common_page(name="about", parent_page=root_page)
        _create_common_page(name="location_based_data", parent_page=root_page)
        _create_common_page(name="whats_coming", parent_page=root_page)
        _create_common_page(name="cookies", parent_page=root_page)
        _create_common_page(name="accessibility_statement", parent_page=root_page)
        _create_common_page(name="compliance", parent_page=root_page)
        whats_new_parent_page = _create_whats_new_parent_page(
            name="whats_new", parent_page=root_page
        )

        _create_bulk_downloads_page(name="bulk_downloads", parent_page=root_page)

        # Create access our data parent and child page
        access_our_data_parent_page = _create_composite_page(
            name="access_our_data_parent_page", parent_page=root_page
        )
        _create_composite_page(
            name="access_our_data_getting_started",
            parent_page=access_our_data_parent_page,
        )

        _create_whats_new_child_entry(
            name="whats_new_soft_launch_of_the_ukhsa_data_dashboard",
            parent_page=whats_new_parent_page,
        )

        create_metrics_documentation_parent_page_and_child_entries()

        weather_health_alerts_page = _create_composite_page(
            name="weather_health_alerts", parent_page=root_page
        )
        _create_composite_page(
            name="heat_health_alerts", parent_page=weather_health_alerts_page
        )
        _create_composite_page(
            name="cold_health_alerts", parent_page=weather_health_alerts_page
        )

    @staticmethod
    def _clear_cms() -> None:
        # Wipe the existing site, pages & badges
        Site.objects.all().delete()
        Badge.objects.all().delete()
        Page.objects.filter(pk__gte=2).delete()  # Wagtail welcome page and all others
