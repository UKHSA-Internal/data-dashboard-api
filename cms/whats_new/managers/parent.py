"""
This file contains the custom QuerySet and Manager classes associated with the `WhatsNewParentPage` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class WhatsNewParentPageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `WhatsNewParentPageManager`"""

    def get_live_pages(self) -> models.QuerySet:
        """Gets all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<WhatsNewParentPageQuerySet [<WhatsNewParentPage: What's New>]>`
        """
        return self.filter(live=True)


class WhatsNewParentPageManager(PageManager):
    """Custom model manager class for the `WhatsNewParentPage` model."""

    def get_queryset(self) -> WhatsNewParentPageQuerySet:
        return WhatsNewParentPageQuerySet(model=self.model, using=self.db)

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<WhatsNewParentPageQuerySet [<WhatsNewParentPage: What's New>]>`
        """
        return self.get_queryset().get_live_pages()
