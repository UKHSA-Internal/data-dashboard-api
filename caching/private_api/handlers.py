import logging
from timeit import default_timer

from caching.common.pages import (
    ALL_PAGE_TYPES,
    collect_all_pages,
    extract_area_selectable_pages,
)
from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.area_selector.orchestration import (
    AreaSelectorOrchestrator,
)
from caching.private_api.management import CacheManagement
from cms.topic.models import TopicPage

logger = logging.getLogger(__name__)


def crawl_all_pages(
    *,
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
    logger.info("Commencing refresh of cache")

    all_pages: ALL_PAGE_TYPES = collect_all_pages()
    private_api_crawler.process_pages(pages=all_pages)

    topic_pages: list[TopicPage] = extract_area_selectable_pages(all_pages=all_pages)
    area_selector_orchestrator.process_pages(pages=topic_pages)

    duration: float = default_timer() - start
    logger.info("Finished refreshing of cache in %s seconds", round(duration, 2))


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


def get_all_downloads(*, file_format: str = "csv") -> list[dict[str, str]]:
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
