"""
Due to the complexity of the Wagtail page tree and programmatic page creation.
The data migration which these handlers feed into are effectively stubbed out.

In Django migrations, the model is referenced via `apps.get_model()`.
This returns the model as it was at that point in time.
The issue is that this model is a frozen version of the model,
which does not have access to any custom methods.

For plain Django models this is fine, but programmatic Wagtail page creation
depends on the `save_revision()` and `publish()` methods, which are not then unavailable.

The solution in our context, is to stub out this migration
and then lean on the `build_cms_site` management command to populate the
data that would have otherwise come from this data migration.

"""

import logging

logger = logging.getLogger(__name__)


def forward_migration_metrics_documentation_models(*args, **kwargs) -> None:
    """Stubbed out data migration. This is now being achieved via the `build_cms_site` management command

    Returns:
        None

    """
    logger.info(
        "This migration has been stubbed out and replaced by the `build_cms_site` management command"
    )


def reverse_migration_metrics_documentation_models(*args, **kwargs) -> None:
    """Stubbed out data migration. This is now being achieved via the `build_cms_site` management command

    Returns:
        None

    """
    logger.info(
        "This migration has been stubbed out and replaced by the `build_cms_site` management command"
    )
