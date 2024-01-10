import logging

from cms.home.models import HomePage
from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page_and_child_entries,
    remove_metrics_documentation_child_entries,
    remove_metrics_documentation_parent_page,
)

logger = logging.getLogger(__name__)


def forward_migration_metrics_documentation_models(apps, schema_editor) -> None:
    """Creates child entries for data migration.

    Notes:
        This will also create the requisite
        `MetricsDocumentationParentPage` model
        if it does not already exist

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    try:
        return create_metrics_documentation_parent_page_and_child_entries()
    except HomePage.DoesNotExist:
        logger.info("No Root page available to create metrics docs parent page with")


def reverse_migration_metrics_documentation_models(apps, schema_editor) -> None:
    """Reverses the child entries migration by removing all entries.

    Args:
        apps: instance of `django.apps.registry.Apps` containing historical models.
        schema_editor: instance of `SchemaEditor`

    Returns:
        None
    """
    remove_metrics_documentation_child_entries()
    remove_metrics_documentation_parent_page()
