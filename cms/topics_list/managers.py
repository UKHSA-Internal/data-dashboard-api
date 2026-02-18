"""
This file contains the custom QuerySet and Manager classes associated with the `TopicsList` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet

EXPECTED_TOPICS_LIST_PAGE_SLUG = "health-topics"


class TopicsListPageQuerySet(PageQuerySet):
    """Custom queryset for which can be used by the `TopicsListPageManager`."""

    def get_topics_list_page(self) -> models.QuerySet:
        """Gets the designated health-topics page.

        Returns:
            QuerySet: A queryset of the individual topics_list page.
                Examples:
                    `<TopicsListPageQuerySet [<TopicsListPage: Health Topics>, ... ]`
        """
        return self.filter(slug=EXPECTED_TOPICS_LIST_PAGE_SLUG)


class TopicsListPageManager(PageManager):
    """Custom model manager class for the `TopicsListPageManager`."""

    def get_queryset(self) -> TopicsListPageQuerySet:
        return TopicsListPageQuerySet(self.model, using=self._db)

    def get_topics_list_page(self):
        """Gets the designated health topics page.

        Returns:
            The designated topics list page object
            which has the slug of `health-topics`
        """
        return self.get_queryset().get_topics_list_page().last()
