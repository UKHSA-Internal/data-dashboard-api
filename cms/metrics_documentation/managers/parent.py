from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class MetricsDocumentationParentPageQuerySet(PageQuerySet):
    """Custom queryset which can by used by the `MetricsDocsParentPageManager"""

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<MetricsDocumentationParentPageQuerySet [MetricsDocumentationParentPage: Metrics Documentation]>`
        """
        return self.filter(live=True)


class MetricsDocumentationParentPageManager(PageManager):
    """Custom model manager class for the `MetricsDocumentationParentPage` mode."""

    def get_queryset(self) -> MetricsDocumentationParentPageQuerySet:
        return MetricsDocumentationParentPageQuerySet(model=self.model, using=self.db)

    def get_live_pages(self) -> models.QuerySet:
        """Gets all currently live pages.

        Returns:
            QuerySet: A Queryset of the live pages:
                `<MetricsDocumentationParentPage [<MetricsDocumentationParentPage: Metrics Documentation]>`
        """
        return self.get_queryset().get_live_pages()
