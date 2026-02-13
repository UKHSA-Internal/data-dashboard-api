"""
This file contains the custom QuerySet and Manager classes associated with the `TopicsList` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet

EXPECTED_LANDING_PAGE_SLUG = "health-topics"

class TopicsListPageQuerySet(PageQuerySet):
    """Custom queryset for which can be used by the `TopicsListPageManager`."""

    def get_live_pages(self) -> models.QuerySet:
        """Gets all currently live pages.

        Returns:
            QuerySet: A queryset of all live pages.
                Examples:
                    `<TopicsListPageQuerySet [<TopicPage: Health Topics>, ]`
        """
        return self.filter(live=True)


class TopicsListPageManager(PageManager):
    """Custom model manager class for the `TopicsListPageManager`."""

    def get_queryset(self) -> models.QuerySet:
        return TopicsListPageQuerySet(self.model, using=self._db)


    def get_live_pages(self):
        """Gets the all currently live pages.

        Returns:
            QuerySet: A queryset of the live pages:
                Examples:
                    `<TopicPageQuerySet [<TopicPage: COVID-19>, <TopicPage: Influenza>, ...]>`
        """
        return self.get_queryset().get_live_pages()
