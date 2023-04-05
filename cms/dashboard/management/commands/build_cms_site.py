import re
import logging

from django.core.management.base import BaseCommand
from typing import List, Dict

from metrics.api.settings import WAGTAIL_SITE_NAME

from wagtail.models import Site, Page
from cms.home.models import HomePage
from cms.common.models import CommonPage
from datetime import datetime

from typing import List, Dict
from bs4 import BeautifulSoup
import glob

logger = logging.getLogger(__name__)


FILE_PATH = "cms/dashboard/pages_to_add/"


def load_html_files() -> Dict[str, str]:
    """
    Import all the html files required for the CMS site

    Args:
        None

    Returns:
        A dictionary of the imported pages. {Page Title : Page Body}

    Raises:
        If a page does not have a title tag then log this fact and move onto the next one
    """
    pages_to_add = glob.glob(FILE_PATH + "*.html")

    result = dict()
    for page in pages_to_add:
        with open(page, "r", encoding="utf-8") as f:
            html_page = f.read()
            parsed_html = BeautifulSoup(html_page, "html5lib")
            if parsed_html.title:
                result[parsed_html.title.text] = parsed_html.body
            else:
                logger.warning(
                    f"CMS Page {page} has no title tag. Page loading skipped"
                )
    return result


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
        home_page = HomePage(title=title, slug=slug)

        # Add this new home page onto the root
        root_page = Page.objects.filter(pk=1).get()
        root_page.add_child(instance=home_page)
        root_page.save_revision().publish()

        # We need to pull the appropriate hostname from somewhere
        # hostname for uat currently ='http://wp-lb-api-1448457284.eu-west-2.elb.amazonaws.com/'
        Site.objects.create(
            hostname="localhost",
            port="80",
            site_name=WAGTAIL_SITE_NAME,
            root_page=root_page,
            is_default_site=True,
        )

        # now add all the other pages
        pages_to_load = load_html_files()

        for page_title, page_body in pages_to_load.items():
            slug = make_slug(page_title=page_title)

            page = CommonPage(
                title=page_title,
                slug=slug,
                date_posted=datetime.now(),
                body=page_body,
            )
            new_page = home_page.add_child(instance=page)
            new_page.save_revision().publish()
