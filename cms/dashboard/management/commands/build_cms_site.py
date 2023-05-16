"""
Utility to build out the basic CMS pages so we don't have to do so manually.
Only intended for use during development
"""

import glob
import json
import logging
import re
from datetime import datetime
from typing import Dict

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from cms.common.models import CommonPage, CommonPageRelatedLink
from cms.home.models import HomePage, HomePageRelatedLink
from cms.topic.models import TopicPage, TopicPageRelatedLink
from metrics.api.settings import ROOT_LEVEL_BASE_DIR, WAGTAIL_SITE_NAME

logger = logging.getLogger(__name__)

FILE_PATH = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/"


def make_slug(page_title: str) -> str:
    """
    Make a CMS Slug from the page title

    Args:
        The page title (taken from the HTML Title Tag for the page)

    Returns:
        The page title as a slug with invalid characters removed.
        Currently only removes quotes, commas and full-stops.
    """

    slug = re.sub("'|\.|\s|,", "-", page_title.lower())
    return slug


def open_example_page_response(page_name: str):
    path = f"{FILE_PATH}{page_name}.json"
    with open(path, "rb") as f:
        return json.load(f)


def _build_related_links(related_link_class, response_data, page) -> None:
    for related_link_response_data in response_data["related_links"]:
        related_link_model = related_link_class(
            page=page,
            title=related_link_response_data["title"],
            url=related_link_response_data["url"],
            body=related_link_response_data["body"],
        )
        related_link_model.save()


def _add_page_to_parent(page: Page, parent_page: HomePage) -> None:
    page = parent_page.add_child(instance=page)
    page.save_revision().publish()


def _build_respiratory_viruses_page(parent_page: Page) -> HomePage:
    data = open_example_page_response(page_name="respiratory_viruses")

    page = HomePage(
        body=data["body"],
        title=data["title"],
        page_description=data["page_description"],
        slug=data["meta"]["slug"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _build_related_links(
        related_link_class=HomePageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _build_topic_page(name: str, parent_page: Page) -> TopicPage:
    data = open_example_page_response(page_name=name)

    page = TopicPage(
        body=data["body"],
        title=data["title"],
        page_description=data["page_description"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
        symptoms=data["symptoms"],
        transmission=data["transmission"],
        treatment=data["treatment"],
        prevention=data["prevention"],
        surveillance_and_reporting=data["surveillance_and_reporting"],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _build_related_links(
        related_link_class=TopicPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


def _build_common_page(name: str, parent_page: Page) -> TopicPage:
    data = open_example_page_response(page_name=name)

    page = CommonPage(
        body=data["body"],
        title=data["title"],
        slug=data["meta"]["slug"],
        date_posted=data["meta"]["first_published_at"].split("T")[0],
    )
    _add_page_to_parent(page=page, parent_page=parent_page)

    _build_related_links(
        related_link_class=CommonPageRelatedLink,
        response_data=data,
        page=page,
    )

    return page


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Wipe the existing CMS pages and load in new ones
        """

        # Wipe the existing site and pages
        Site.objects.all().delete()
        Page.objects.filter(pk__gte=2).delete()  # Wagtail welcome page and all others

        # Make a new home page
        title = "UKHSA Dashboard Root"
        slug = make_slug(page_title=title)
        root_page = HomePage(title=title, slug=slug)

        # Add this new home page onto the root
        wagtail_root_page = Page.get_first_root_node()
        wagtail_root_page.add_child(instance=root_page)
        wagtail_root_page.save_revision().publish()

        Site.objects.create(
            hostname="localhost",
            port="80",
            site_name=WAGTAIL_SITE_NAME,
            root_page=wagtail_root_page,
            is_default_site=True,
        )

        respiratory_viruses_page: HomePage = _build_respiratory_viruses_page(
            parent_page=root_page
        )
        _build_topic_page(name="coronavirus", parent_page=respiratory_viruses_page)
        _build_topic_page(name="influenza", parent_page=respiratory_viruses_page)
        _build_topic_page(
            name="other_respiratory_viruses", parent_page=respiratory_viruses_page
        )
        _build_common_page(name="about", parent_page=respiratory_viruses_page)
        _build_common_page(name="maps", parent_page=respiratory_viruses_page)
        _build_common_page(
            name="how_to_use_this_data", parent_page=respiratory_viruses_page
        )
        _build_common_page(name="whats_new", parent_page=respiratory_viruses_page)
