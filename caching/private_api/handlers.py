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


def force_cache_refresh_for_all_pages(
    *,
    cache_management: CacheManagement | None = None,
    private_api_crawler: PrivateAPICrawler | None = None,
) -> None:
    """Forcibly refresh the cache for all pages

    Args:
        `cache_management`: A `CacheManagement` object
            which will be used to clear the cache
            prior to filling the cache again.
            Defaults to a concrete `CacheManagement` object
        `private_api_crawler`: A `PrivateAPICrawler` object
            which will be used to process the pages.
            Defaults to an object with an `InternalAPIClient`
            set to force cache refreshes.

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
    cache_management = cache_management or CacheManagement(in_memory=False)
    logger.info("Clearing all non reserved keys")
    cache_management.clear_non_reserved_keys()

    private_api_crawler = (
        private_api_crawler or PrivateAPICrawler.create_crawler_for_default_cache()
    )
    area_selector_orchestrator = AreaSelectorOrchestrator(
        geographies_api_crawler=private_api_crawler.geography_api_crawler
    )
    crawl_all_pages(
        private_api_crawler=private_api_crawler,
        area_selector_orchestrator=area_selector_orchestrator,
    )


def force_cache_refresh_for_reserved_namespace(
    *,
    cache_management: CacheManagement | None = None,
    private_api_crawler: PrivateAPICrawler | None = None,
) -> None:
    """Forcibly refresh the cache for the reserved namespace only.

    Args:
        `cache_management`: A `CacheManagement` object
            which will be used to clear the cache
            prior to filling the cache again.
            Defaults to a concrete `CacheManagement` object
        `private_api_crawler`: A `PrivateAPICrawler` object
            which will be used to process the pages.
            Defaults to an object with an `InternalAPIClient`
            set to force cache refreshes.

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

        This will write to the cache 1 by 1,
        and will only target the reserved namespace.

        All new keys are first written to the staging namespace,
        and then moved into the reserved namespace when ready.

    Returns:
        None

    """
    cache_management = cache_management or CacheManagement(in_memory=False)
    private_api_crawler = (
        private_api_crawler or PrivateAPICrawler.create_crawler_for_reserved_cache()
    )
    area_selector_orchestrator = AreaSelectorOrchestrator(
        geographies_api_crawler=private_api_crawler.geography_api_crawler
    )

    original_reserved_keys: list[str] = cache_management.get_reserved_keys()
    crawl_all_pages(
        private_api_crawler=private_api_crawler,
        area_selector_orchestrator=area_selector_orchestrator,
    )
    cache_management.delete_many(keys=original_reserved_keys)
    cache_management.move_all_reserved_staging_keys_into_reserved_namespace()


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
    crawler = PrivateAPICrawler.create_crawler_for_default_cache()
    return crawler.get_all_downloads(pages=pages, file_format=file_format)
