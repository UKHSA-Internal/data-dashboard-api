import logging
import os
from timeit import default_timer

from django.db.models import Manager

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.area_selector.orchestration import (
    AreaSelectorOrchestrator,
)
from caching.private_api.management import CacheManagement
from cms.common.models import CommonPage
from cms.home.models import HomePage
from cms.topic.models import TopicPage
from cms.whats_new.models import WhatsNewChildEntry, WhatsNewParentPage

DEFAULT_HOME_PAGE_MANAGER = HomePage.objects
DEFAULT_TOPIC_PAGE_MANAGER = TopicPage.objects
DEFAULT_COMMON_PAGE_MANAGER = CommonPage.objects
DEFAULT_WHATS_NEW_PARENT_PAGE_MANAGER = WhatsNewParentPage.objects
DEFAULT_WHATS_NEW_CHILD_ENTRY_MANAGER = WhatsNewChildEntry.objects


logger = logging.getLogger(__name__)

ALL_PAGE_TYPES = list[HomePage, TopicPage, WhatsNewParentPage, WhatsNewChildEntry]


def collect_all_pages(
    home_page_manager: Manager = DEFAULT_HOME_PAGE_MANAGER,
    topic_page_manager: Manager = DEFAULT_TOPIC_PAGE_MANAGER,
    common_page_manager: Manager = DEFAULT_COMMON_PAGE_MANAGER,
    whats_new_parent_page_manager: Manager = DEFAULT_WHATS_NEW_PARENT_PAGE_MANAGER,
    whats_new_child_entry_manager: Manager = DEFAULT_WHATS_NEW_CHILD_ENTRY_MANAGER,
) -> ALL_PAGE_TYPES:
    """Collects and returns all pages which should be processed for caching

    Args:
        home_page_manager: The model manager for the `HomePage` model
            Defaults to the concrete `HomePageManager`
            via `HomePage.objects`
        topic_page_manager: The model manager for the `TopicPage` model
            Defaults to the concrete `TopicPageManager`
            via `TopicPage.objects`
        common_page_manager: The model manager for the `CommonPage` model
            Defaults to the concrete `CommonPageManager`
            via `CommonPage.objects`
        whats_new_parent_page_manager: The model manager for the `WhatsNewParentPage` model
            Defaults to the concrete `WhatsNewParentPageManager`
            via `WhatsNewParentPage.objects`
        whats_new_child_entry_manager: The model manager for the `WhatsNewChildEntry` model
            Defaults to the concrete `WhatsNewChildEntryManager`
            via `WhatsNewEntryPage.objects`

    Returns:
        List of `Page` objects which are to be processed for caching

    """
    landing_page: HomePage = home_page_manager.get_landing_page()
    pages = [] if landing_page is None else [landing_page]
    pages += topic_page_manager.get_live_pages()
    pages += common_page_manager.get_live_pages()
    pages += whats_new_parent_page_manager.get_live_pages()
    pages += whats_new_child_entry_manager.get_live_pages()

    return pages


def extract_area_selectable_pages(
    all_pages: ALL_PAGE_TYPES,
) -> list[TopicPage]:
    """Builds a new list containing only the pages which are deemed suitable for the area selector

    Args:
        all_pages: Iterable of a mixture of page types

    Returns:
        List of pages which are deemed suitable for
        the area selector from within the given
        `all_pages` iterable

    """
    return [page for page in all_pages if isinstance(page, TopicPage)]
    return [
        page for page in all_pages if getattr(page, "is_valid_for_area_selector", False)
    ]


def crawl_all_pages(
    private_api_crawler: PrivateAPICrawler,
    area_selector_orchestrator: AreaSelectorOrchestrator,
) -> None:
    """Parses the CMS blocks for all pages with the given `crawler`

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

    Args:
        private_api_crawler: A `PrivateAPICrawler` object which will be used
            to process and crawl the various CMS blocks
            which are required to parse each page
        area_selector_orchestrator: An `AreaSelectorOrchestrator` object
            which is used to orchestrate parallel `PrivateAPICrawler` objects
            as workers to process geography/page combinations

    Returns:
        None

    """
    start: float = default_timer()
    logging.info("Commencing refresh of cache")

    all_pages: ALL_PAGE_TYPES = collect_all_pages()
    private_api_crawler.process_pages(pages=all_pages)

    if os.environ.get("ENABLE_AREA_SELECTOR"):
        topic_pages: list[TopicPage] = extract_area_selectable_pages(
            all_pages=all_pages
        )
        area_selector_orchestrator.process_pages(pages=topic_pages)

    duration: float = default_timer() - start
    logging.info("Finished refreshing of cache in %s seconds", round(duration, 2))


def check_cache_for_all_pages() -> None:
    """Checks the cache for all pages but does not calculate responses

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

    Returns:
        None

    Raises:
        `CacheCheckResultedInMissError`: If any cache misses occur.
            Note that this will error at the 1st cache miss.

    """
    private_api_crawler = PrivateAPICrawler.create_crawler_for_cache_checking_only()
    area_selector_orchestrator = AreaSelectorOrchestrator(
        geographies_api_crawler=private_api_crawler.geography_api_crawler
    )

    crawl_all_pages(
        private_api_crawler=private_api_crawler,
        area_selector_orchestrator=area_selector_orchestrator,
    )


def force_cache_refresh_for_all_pages() -> None:
    """Forcibly refresh the cache for all pages

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

        This will write to the cache 1 by 1.
        This currently does not support blue/green cache hydration.
        As such, if the cache is hit during the invocation of this,
        then it is feasible that the request will be routed to the origin

    Returns:
        None

    """
    cache_management = CacheManagement(in_memory=False)
    cache_management.clear()

    private_api_crawler = PrivateAPICrawler.create_crawler_for_force_cache_refresh()
    area_selector_orchestrator = AreaSelectorOrchestrator(
        geographies_api_crawler=private_api_crawler.geography_api_crawler
    )
    crawl_all_pages(
        private_api_crawler=private_api_crawler,
        area_selector_orchestrator=area_selector_orchestrator,
    )


def get_all_downloads(file_format: str = "csv") -> list[dict[str, str]]:
    """Get all downloads from chart cards on supported pages

    Args:
        file_format: the format for download response data supports csv and json
            defaults to csv.

    Notes:
        You can pass all pages to the crawler's `get_all_downloads'
        and it will skip over any that don't contain chart data
        skipped pages will be logged.

    Returns:
       A list of dictionaries containing a filename and download content.

    """
    pages = collect_all_pages()
    crawler = PrivateAPICrawler.create_crawler_for_lazy_loading()
    return crawler.get_all_downloads(pages=pages, file_format=file_format)
