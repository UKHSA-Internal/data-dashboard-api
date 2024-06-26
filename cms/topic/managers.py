"""
This file contains the custom QuerySet and Manager classes associated with the `TopicPage` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class TopicPageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `TopicPageManager`"""

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<TopicPageQuerySet [<TopicPage: COVID-19>, <TopicPage: Influenza>, ...]>`
        """
        return self.filter(live=True)


class TopicPageManager(PageManager):
    """Custom model manager class for the `TopicPage` model."""

    def get_queryset(self) -> TopicPageQuerySet:
        return TopicPageQuerySet(model=self.model, using=self.db)

    def get_live_pages(self) -> models.QuerySet:
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<TopicPageQuerySet [<TopicPage: COVID-19>, <TopicPage: Influenza>, ...]>`
        """
        return self.get_queryset().get_live_pages()
