import logging
from timeit import default_timer
from typing import Optional

from django.db.models import Manager
from wagtail.models import Page

from caching.crawler import Crawler
from cms.home.models import HomePage
from cms.topic.models import TopicPage

DEFAULT_HOME_PAGE_MANAGER = HomePage.objects
DEFAULT_TOPIC_PAGE_MANAGER = TopicPage.objects

logger = logging.getLogger(__name__)


def collect_all_pages(
    home_page_manager: Manager = DEFAULT_HOME_PAGE_MANAGER,
    topic_page_manager: Manager = DEFAULT_TOPIC_PAGE_MANAGER,
) -> list[HomePage, TopicPage]:
    """Collects and returns all pages which should be processed for caching

    Args:
        home_page_manager: The model manager for the `HomePage` model
            Defaults to the concrete `HomePageManager`
            via `HomePage.objects`
        topic_page_manager: The model manager for the `TopicPage` model
            Defaults to the concrete `TopicPageManager`
            via `TopicPage.objects`

    Returns:
        List of `Page` objects which are to be processed for caching

    """
    landing_page: HomePage = home_page_manager.get_landing_page()
    pages = [] if landing_page is None else [landing_page]
    pages += topic_page_manager.get_live_pages()
    return pages


def crawl_all_pages(crawler: Crawler) -> None:
    """Rehydrate the cache for all pages

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

    Returns:
        None

    """
    start: float = default_timer()
    logging.info("Commencing refresh of cache")

    pages: list[HomePage, TopicPage] = collect_all_pages()
    crawl_pages(pages=pages)

    duration: float = default_timer() - start
    logging.info(f"Finished refreshing of cache in {round(duration, 2)}s")
