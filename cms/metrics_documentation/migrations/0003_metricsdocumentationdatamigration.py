import datetime
import json

from cms.metrics_documentation.models import (
    MetricsDocumentationChildEntry,
    MetricsDocumentationParentPage,
)
from cms.metrics_documentation.utils import get_metrics_definitions
from cms.home.models import HomePage
from django.db import migrations, models
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

FILE_PATH = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/"


def load_metric_documentation_parent_page():
    """Returns a JSON Object of metrics documentation parent page date.

    Returns:
        JSON Object containing parent page data.
    """
    path = f"{FILE_PATH}metrics_documentation.json"
    with open(path, "rb") as file:
        return json.load(file)


def forward_metric_documentation_parent(apps, schema_editor) -> None:
    """Creates parent page for data migration.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    try:
        MetricsDocumentationParentPage.objects.get()
    except MetricsDocumentationParentPage.DoesNotExist:
        root_page = HomePage.objects.last()
        parent_page_data = load_metric_documentation_parent_page()
        metrics_parent = MetricsDocumentationParentPage(
            title=parent_page_data["title"],
            depth=1,
            date_posted=datetime.datetime.today(),
            body=parent_page_data["body"],
        )
        root_page.add_child(instance=metrics_parent)
        metrics_parent.save()


def reverse_metric_documentation_parent(apps, schema_editor) -> None:
    """Reverse the parent page migration by removing the entry.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    MetricsDocumentationParentPage.objects.all().delete()


def forward_metric_documentation_child_entries(apps, schema_editor) -> None:
    """Creates child entries for data migration.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    entries = get_metrics_definitions()
    root_page = MetricsDocumentationParentPage.objects.last()
    for entry in entries:
        metrics_child = MetricsDocumentationChildEntry(**entry)
        root_page.add_child(instance=metrics_child)
        metrics_child.save()


def reverse_metric_documentation_child_entries(apps, schema_editor) -> None:
    """Reverses the child entries migration by removing all entries.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    MetricsDocumentationChildEntry.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("metrics_documentation", "0002_metricsdocumentationchildentry")]

    operations = [
        migrations.RunPython(
            code=forward_metric_documentation_parent,
            reverse_code=reverse_metric_documentation_parent,
        ),
        migrations.RunPython(
            code=forward_metric_documentation_child_entries,
            reverse_code=reverse_metric_documentation_child_entries,
        ),
    ]
