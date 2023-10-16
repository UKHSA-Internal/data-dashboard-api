import logging
from timeit import default_timer

from django.db.models import Manager

from caching.private_api.crawler import PrivateAPICrawler
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


def _crawl_all_pages(crawler: PrivateAPICrawler) -> None:
    """Parses the CMS blocks for all pages with the given `crawler`

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

    Args:
        crawler: A `Crawler` object which will be used to
            orchestrate the various calls required to parse each page

    Returns:
        None

    """
    start: float = default_timer()
    logging.info("Commencing refresh of cache")

    pages: ALL_PAGE_TYPES = collect_all_pages()
    crawler.process_pages(pages=pages)

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
    crawler = PrivateAPICrawler.create_crawler_for_cache_checking_only()
    _crawl_all_pages(crawler=crawler)


def force_cache_refresh_for_all_pages() -> None:
    """Forcibly refresh the cache for all pages

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

        This will overwrite existing entries in the cache 1 by 1.
        This currently does not support blue/green cache hydration.
        As such, if the cache is hit during the invocation of this,
        then it is feasible that the cache will contain 1 stale half
        and another fresh half of items.

    Returns:
        None

    """
    crawler = PrivateAPICrawler.create_crawler_for_force_cache_refresh()
    _crawl_all_pages(crawler=crawler)


def get_all_downloads() -> None:
    """Forcibly refresh the cache for all pages

    Notes:
        Currently "all pages" means the following:
        - The home page with the slug of "dashboard"
        - All live/published topic pages

        This will overwrite existing entries in the cache 1 by 1.
        This currently does not support blue/green cache hydration.
        As such, if the cache is hit during the invocation of this,
        then it is feasible that the cache will contain 1 stale half
        and another fresh half of items.

    Returns:
        None

    """
    crawler = PrivateAPICrawler.create_crawler_for_force_cache_refresh()
    _crawl_all_pages(crawler=crawler)
