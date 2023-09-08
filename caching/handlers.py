from django.db.models import Manager

from cms.home.models import HomePage
from cms.topic.models import TopicPage

DEFAULT_HOME_PAGE_MANAGER = HomePage.objects
DEFAULT_TOPIC_PAGE_MANAGER = TopicPage.objects


def collect_all_pages(
    home_page_manager: Manager = DEFAULT_TOPIC_PAGE_MANAGER,
    topic_page_manager: Manager = DEFAULT_TOPIC_PAGE_MANAGER,
) -> list[HomePage | TopicPage]:
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
    pages = [home_page_manager.get_landing_page()]
    pages += topic_page_manager.get_live_pages()
    return pages
