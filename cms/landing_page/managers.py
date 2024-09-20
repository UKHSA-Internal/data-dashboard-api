from django.db import models
from wagtail.models import PageManager
from wagtail.query import PageQuerySet

EXPECTED_LANDING_PAGE_SLUG = "data_dashboard"


class LandingPageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `LandingPageManager`"""

    def get_landing_page(self) -> models.QuerySet:
        """Gets the designated landing page.

        Returns:
            QuerySet: A queryset of the individual landing page:
                Examples:
                    `<PageQuerySet [<landingPage: UKHSA data dashboard>]>`
        """
        return self.filter(slug=EXPECTED_LANDING_PAGE_SLUG)


class LandingPageManager(PageManager):
    """Custom model manager  class for the `LandingPage` model."""

    def get_query(self) -> LandingPageQuerySet:
        return LandingPageQuerySet(model=self.model, using=self.db)

    def get_landing_page(self) -> "LandingPage":
        """Gets the designated landing page.

        Returns:
            The designated landing page object
            which has the slug of `data-dashboard`
        """
        return self.get_queryset().get_landing_page().last()
