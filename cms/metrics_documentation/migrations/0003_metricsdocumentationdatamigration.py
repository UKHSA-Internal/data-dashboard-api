import logging

from cms.metrics_documentation.models import (
    MetricsDocumentationParentPage,
)
from cms.home.models import HomePage
from django.db import migrations

from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page,
    create_metrics_documentation_child_entries,
    remove_metrics_documentation_child_entries,
)


logger = logging.getLogger(__name__)


def forward_migration_metrics_documentation_parent_page(apps, schema_editor) -> None:
    """Creates parent page for data migration if one doesn't exist.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    try:
        return create_metrics_documentation_parent_page()
    except HomePage.DoesNotExist:
        logger.info("No Root page available to create metrics docs parent page with")


def forward_migration_metrics_documentation_child_entries(apps, schema_editor) -> None:
    """Creates child entries for data migration.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    try:
        return create_metrics_documentation_child_entries()
    except MetricsDocumentationParentPage.DoesNotExist:
        logger.info(
            "No metrics docs parent page available to create child entries with"
        )


def reverse_migration_metrics_documentation_child_entries(apps, schema_editor) -> None:
    """Reverses the child entries migration by removing all entries.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    remove_metrics_documentation_child_entries()


class Migration(migrations.Migration):
    dependencies = [("metrics_documentation", "0002_metricsdocumentationchildentry")]

    operations = [
        migrations.RunPython(
            code=forward_migration_metrics_documentation_parent_page,
        ),
        migrations.RunPython(
            code=forward_migration_metrics_documentation_child_entries,
            reverse_code=reverse_migration_metrics_documentation_child_entries,
        ),
    ]
