import datetime
import json
import logging

from django.core.exceptions import ValidationError
from django.db.models import Manager
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


DEFAULT_METRICS_DOCUMENTATION_PARENT_PAGE_MANAGER = (
    MetricsDocumentationParentPage.objects
)


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


def get_or_create_metrics_documentation_parent_page(
    metrics_documentation_parent_page_manager: Manager = DEFAULT_METRICS_DOCUMENTATION_PARENT_PAGE_MANAGER,
) -> MetricsDocumentationParentPage:
    """Creates parent page for data migration if one doesn't exist.

    Args:
        `metrics_documentation_parent_page_manager`: The model manager
            for the `MetricsDocumentationParentPage` model.
            Defaults to the concrete manager
            on `MetricsDocumentationParentPage.objects`

    Returns:
        The fetched or created `MetricsDocumentationParentPage` model

    Raises:
        `HomePage.DoesNotExist`: If there is no root page model
            with the reserved slug of "ukhsa-dashboard-root".
            This typically happens when the application
            is being bootstrapped for the first time

    """
    try:
        return metrics_documentation_parent_page_manager.get(
            slug="metrics-documentation"
        )
    except MetricsDocumentationParentPage.DoesNotExist:
        return _create_metrics_documentation_parent_page()


def _create_metrics_documentation_parent_page():
    root_page = HomePage.objects.get(slug="ukhsa-dashboard-root")
    parent_page_data = load_metric_documentation_parent_page()
    metrics_parent = MetricsDocumentationParentPage(
        title=parent_page_data["title"],
        date_posted=datetime.datetime.today(),
        body=parent_page_data["body"],
        show_in_menus=False,
    )
    _add_page_as_subpage_to_parent(subpage=metrics_parent, parent_page=root_page)
    return metrics_parent


def create_metrics_documentation_parent_page_and_child_entries() -> None:
    """Creates the parent page & child entries for the metrics documentation app.

    Notes:
        - This will also create the requisite
          `MetricsDocumentationParentPage` model
          if it does not already exist
        - This will also delete any existing
          `MetricsDocumentationChildEntry` records
          prior to creating the new child entries.

    Returns:
        None

    Raises:
        `HomePage.DoesNotExist`: If there is no root page model
            with the reserved slug of "ukhsa-dashboard-root".
            This typically happens when the migrations
            are being applied to an empty application
            and has not been bootstrapped yet.

    """
    entries: list[dict[str | list[dict]]] = get_metrics_definitions()
    parent_page = get_or_create_metrics_documentation_parent_page()

    remove_metrics_documentation_child_entries()

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
        except ValidationError:
            logger.warning(
                "Metrics Documentation Child Entry for %s was not created. "
                "Because the corresponding `Metric` was not created beforehand",
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
