import datetime
import json
import logging

from wagtail.models import Page

from cms.home.models import HomePage
from cms.metrics_documentation.data_migration.child_entries import (
    get_metrics_definitions,
)
from cms.metrics_documentation.models import (
    MetricsDocumentationChildEntry,
    MetricsDocumentationParentPage,
)
from cms.metrics_documentation.models.child import (
    InvalidTopicForChosenMetricForChildEntryError,
)
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

logger = logging.getLogger(__name__)


def load_metric_documentation_parent_page() -> dict:
    """Returns a JSON Object of metrics documentation parent page date.

    Returns:
        JSON Object containing parent page data.
    """
    path = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/metrics_documentation.json"
    with open(path, "rb") as file:
        return json.load(file)


def _add_page_as_subpage_to_parent(subpage: Page, parent_page: HomePage) -> None:
    subpage = parent_page.add_child(instance=subpage)
    subpage.save_revision().publish()


def create_metrics_documentation_parent_page() -> None:
    """Creates parent page for data migration if one doesn't exist.

    Returns:
        None

    Raises:
        `HomePage.DoesNotExist`: If there is no root page model
            with the reserved slug of "ukhsa-dashboard-root".
            This typically happens when the application
            is being bootstrapped for the first time

    """
    try:
        return MetricsDocumentationParentPage.objects.get(slug="metrics-documentation")
    except MetricsDocumentationParentPage.DoesNotExist:
        root_page = HomePage.objects.get(slug="ukhsa-dashboard-root")
        parent_page_data = load_metric_documentation_parent_page()
        metrics_parent = MetricsDocumentationParentPage(
            title=parent_page_data["title"],
            date_posted=datetime.datetime.today(),
            body=parent_page_data["body"],
        )
        _add_page_as_subpage_to_parent(subpage=metrics_parent, parent_page=root_page)


def create_metrics_documentation_child_entries() -> None:
    """Creates child entries for data migration.

    Returns:
        None

    Raises:
        `MetricsDocumentationParentPage.DoesNotExist`: If
            there is no parent page model with the
            reserved slug of "metrics-documentation".
            This typically happens when the application
            is being bootstrapped for the first time

    """
    entries: list[dict[str | list[dict]]] = get_metrics_definitions()
    parent_page = MetricsDocumentationParentPage.objects.get(
        slug="metrics-documentation"
    )
    for entry in entries:
        metrics_child = MetricsDocumentationChildEntry(**entry)
        try:
            _add_page_as_subpage_to_parent(
                subpage=metrics_child, parent_page=parent_page
            )
        except (InvalidTopicForChosenMetricForChildEntryError, AttributeError):
            logger.warning(
                "Metrics Documentation Child Entry for %s was not created. "
                "Because the corresponding `Topic` was not created beforehand",
                entry["metric"],
            )


def remove_metrics_documentation_child_entries() -> None:
    """Removes all `MetricsDocumentationChildEntry` record from the database

    Returns:
        None

    """
    MetricsDocumentationChildEntry.objects.all().delete()


def remove_metrics_documentation_parent_page() -> None:
    """Removes the `MetricsDocumentationParentPage` record from the database

    Returns:
        None

    """
    MetricsDocumentationParentPage.objects.all().delete()
