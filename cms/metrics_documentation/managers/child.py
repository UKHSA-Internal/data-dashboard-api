from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class MetricsDocumentationChildEntryQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `MetricsDocumentationChildEntryManager"""

    def get_live_pages(self) -> models.QuerySet:
        """Gets all current live pages.

        Returns:
            QuerySet: A queryset of live pages:
                Examples:
                    `<MetricsDocumentationChildEntryQuerySet [<MetricsDocumentationChildEntry, ...]>`
        """
        return self.filter(live=True)


class MetricsDocumentationChildEntryManager(PageManager):
    """Custom model manager class for the `MetricsDocumentationChildEntry` model."""

    def get_queryset(self) -> MetricsDocumentationChildEntryQuerySet:
        return MetricsDocumentationChildEntryManager(model=self.model, using=self.db)

    def get_live_pages(self) -> models.QuerySet:
        """Gets all current live pages.

        Returns:
            QuerySet: A QuerySet of the live pages.
                Examples:
                    `<MetricsDocumentationChildEntryQuerySet [<MetricsDocumentation: ..., ...]>`
        """
        return self.get_queryset().get_live_pages()
