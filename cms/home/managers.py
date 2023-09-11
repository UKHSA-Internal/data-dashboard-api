"""
This file contains the custom QuerySet and Manager classes associated with the `HomePage` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet

EXPECTED_HOME_PAGE_SLUG = "dashboard"


class HomePageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `HomePageManager`"""

    def get_landing_page(self) -> models.QuerySet:
        """Gets the designated landing page.

        Returns:
            QuerySet: A queryset of the individual landing page:
                Examples:
                    `<PageQuerySet [<HomePage: UKHSA data dashboard>]>`
        """
        return self.filter(slug=EXPECTED_HOME_PAGE_SLUG)


class HomePageManager(PageManager):
    """Custom model manager class for the `HomePage` model."""

    def get_queryset(self) -> HomePageQuerySet:
        return HomePageQuerySet(model=self.model, using=self.db)

    def get_landing_page(self) -> "HomePage":
        """Gets the designated landing page.

        Returns:
            The designated landing page object
            which has the slug of `dashboard`

        """
        return self.get_queryset().get_landing_page().last()
