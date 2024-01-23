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

    def get_covid_page(self) -> models.QuerySet:
        """Gets the COVID-19 from the currently live pages

        Returns:
            QuerySet: A queryset of the live COVID-19 pages:
                Examples:
                    `<TopicPageQuerySet [<TopicPage: COVID-19>]>`
        """
        return self.get_live_pages().filter(title="COVID-19")


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

    def get_covid_page(self):
        """Gets the COVID-19 from the currently live pages

        Returns:
            The currently live COVID-19 page.
            Or None if no COVID-19 page is available

        """
        return self.get_live_pages().filter(title="COVID-19").first()
