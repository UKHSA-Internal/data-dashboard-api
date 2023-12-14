import datetime
import json

from cms.home.models import HomePage
from cms.metrics_documentation.data_migration.import_child_entries import (
    get_metrics_definitions,
)
from cms.metrics_documentation.models import (
    MetricsDocumentationChildEntry,
    MetricsDocumentationParentPage,
)
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

FILE_PATH = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/"


def load_metric_documentation_parent_page() -> dict:
    """Returns a JSON Object of metrics documentation parent page date.

    Returns:
        JSON Object containing parent page data.
    """
    path = f"{FILE_PATH}metrics_documentation.json"
    with open(path, "rb") as file:
        return json.load(file)


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
        metrics_parent = root_page.add_child(instance=metrics_parent)
        metrics_parent.save_revision().publish()


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
    entries = get_metrics_definitions()
    parent_page = MetricsDocumentationParentPage.objects.get(
        slug="metrics-documentation"
    )
    for entry in entries:
        metrics_child = MetricsDocumentationChildEntry(**entry)
        metrics_child = parent_page.add_child(instance=metrics_child)
        metrics_child.save_revision().publish()


def remove_metrics_documentation_child_entries() -> None:
    """Removes all `MetricsDocumentationChildEntry` record from the database

    Returns:
        None

    """
    MetricsDocumentationChildEntry.objects.all().delete()
