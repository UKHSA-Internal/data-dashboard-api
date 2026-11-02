from django.db.models import Manager

from cms.auth_content.page_filtering import filter_pages_for_permissions
from cms.common.models import CommonPage
from cms.topic.models import TopicPage
from cms.whats_new.models import WhatsNewChildEntry, WhatsNewParentPage
from common.auth.permissions import PermissionSetsType

DEFAULT_TOPIC_PAGE_MANAGER = TopicPage.objects
DEFAULT_COMMON_PAGE_MANAGER = CommonPage.objects
DEFAULT_WHATS_NEW_PARENT_PAGE_MANAGER = WhatsNewParentPage.objects
DEFAULT_WHATS_NEW_CHILD_ENTRY_MANAGER = WhatsNewChildEntry.objects

ALL_PAGE_TYPES = list[TopicPage, WhatsNewParentPage, WhatsNewChildEntry]


def collect_all_pages(
    *,
    topic_page_manager: Manager = DEFAULT_TOPIC_PAGE_MANAGER,
    common_page_manager: Manager = DEFAULT_COMMON_PAGE_MANAGER,
    whats_new_parent_page_manager: Manager = DEFAULT_WHATS_NEW_PARENT_PAGE_MANAGER,
    whats_new_child_entry_manager: Manager = DEFAULT_WHATS_NEW_CHILD_ENTRY_MANAGER,
) -> ALL_PAGE_TYPES:
    """Collects and returns all pages which should be processed for caching

    Args:
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
    pages = []
    pages += topic_page_manager.get_live_pages()
    pages += common_page_manager.get_live_pages()
    pages += whats_new_parent_page_manager.get_live_pages()
    pages += whats_new_child_entry_manager.get_live_pages()

    return pages


def collect_viewable_pages(
    *,
    permission_sets: PermissionSetsType | None = None,
    topic_page_manager: Manager = DEFAULT_TOPIC_PAGE_MANAGER,
    common_page_manager: Manager = DEFAULT_COMMON_PAGE_MANAGER,
    whats_new_parent_page_manager: Manager = DEFAULT_WHATS_NEW_PARENT_PAGE_MANAGER,
    whats_new_child_entry_manager: Manager = DEFAULT_WHATS_NEW_CHILD_ENTRY_MANAGER,
) -> ALL_PAGE_TYPES:
    """Collects and returns all live pages which can be viewed with the given `permission_sets`

    Notes:
        Non-public pages are only included
        when the given `permission_sets` allow for them.
        If no `permission_sets` are provided,
        i.e. the request was made by an anonymous/unauthenticated user,
        then only public pages are returned.

    Args:
        permission_sets: The permission sets extracted
            from the request of the end user.
            Defaults to None, in which case
            only public pages are returned
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
        List of `Page` objects which can be viewed
        by the owner of the given `permission_sets`

    """
    page_managers: list[Manager] = [
        topic_page_manager,
        common_page_manager,
        whats_new_parent_page_manager,
        whats_new_child_entry_manager,
    ]

    pages = []
    for page_manager in page_managers:
        pages += filter_pages_for_permissions(
            queryset=page_manager.get_live_pages(),
            permission_sets=permission_sets,
        )

    return pages


def extract_area_selectable_pages(*, all_pages: ALL_PAGE_TYPES) -> list[TopicPage]:
    """Builds a new list containing only the pages which are deemed suitable for the area selector

    Args:
        all_pages: Iterable of a mixture of page types

    Returns:
        List of pages which are deemed suitable for
        the area selector from within the given
        `all_pages` iterable

    """
    return [
        page for page in all_pages if getattr(page, "is_valid_for_area_selector", False)
    ]


def get_pages_for_area_selector() -> list[TopicPage]:
    """Builds a list of pages which are deemed suitable for the area selector

    Returns:
        List of pages which are deemed suitable for
        the area selector

    """
    all_pages: ALL_PAGE_TYPES = collect_all_pages()
    return extract_area_selectable_pages(all_pages=all_pages)
