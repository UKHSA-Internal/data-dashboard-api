"""
This file contains the custom QuerySet and Manager classes associated with the `CommonPage` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class CommonPageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `CommonPageManager`"""

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<CommonPageQuerySet [<CommonPage: About>, <CommonPage: Compliance>, ...]>`
        """
        return self.filter(live=True)


class CommonPageManager(PageManager):
    """Custom model manager class for the `CommonPage` model."""

    def get_queryset(self) -> CommonPageQuerySet:
        return CommonPageQuerySet(model=self.model, using=self.db)

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<CommonPageQuerySet [<CommonPage: About>, <CommonPage: Compliance>, ...]>`
        """
        return self.get_queryset().get_live_pages()
