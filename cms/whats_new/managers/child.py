"""
This file contains the custom QuerySet and Manager classes associated with the `WhatsNewChildEntry` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class WhatsNewChildEntryQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `WhatsNewChildEntryManager`"""

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<WhatsNewChildEntryQuerySet [<WhatsNewChildEntry: Data Issue 11th Oct>, ...]>`
        """
        return self.filter(live=True)


class WhatsNewChildEntryManager(PageManager):
    """Custom model manager class for the `WhatsNewChildEntry` model."""

    def get_queryset(self) -> WhatsNewChildEntryQuerySet:
        return WhatsNewChildEntryQuerySet(model=self.model, using=self.db)

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<WhatsNewChildEntryQuerySet [<WhatsNewChildEntry: Data Issue 11th Oct>, ...]>`
        """
        return self.get_queryset().get_live_pages()
