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

from cms.metrics_documentation.data_migration.operations import create_metrics_documentation_parent_page, create_metrics_documentation_child_entries
FILE_PATH = f"{ROOT_LEVEL_BASE_DIR}/cms/dashboard/templates/cms_starting_pages/"




class RootPageDoesNotExist:
    def __init__(self):
        message = "There is no home page to act as your entries root."
        super().__init__(message)


def forward_migration_parent_entry(apps, schema_editor) -> None:
    """Creates parent page for data migration if one doesn't exist.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    try:
        create_metrics_documentation_parent_page()
        #HomePage.objects.get(slug="ukhsa_dashboard_root")
    except HomePage.DoesNotExist:
        print("no home page to act as root")
        return

    print("testing testing 123")
    # call build metrics_documentation_parent_entry()


def forward_metric_documentation_parent(apps, schema_editor) -> None:
    """moved to operations
    """
    # move this out to new create function - do this for child as well
    # this function, try/except for calling the new function
    # give an error

        # if root_page == none raise error. custom error.


def forward_metric_documentation_child_entries(apps, schema_editor) -> None:
    """Creates child entries for data migration.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    try:
        create_metrics_documentation_child_entries()
        #HomePage.objects.get(slug="ukhsa_dashboard_root")
    except MetricsDocumentationParentPage.DoesNotExist:
        print("no parent page to act as root")
        return


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
            code=forward_migration_parent_entry,
        ),
        migrations.RunPython(
            code=forward_metric_documentation_child_entries,
            reverse_code=reverse_metric_documentation_child_entries,
        ),
    ]
