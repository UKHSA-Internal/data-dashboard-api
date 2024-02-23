"""
This file contains the custom QuerySet and Manager classes associated with the `CompositePage` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from wagtail.models import PageManager
from wagtail.query import PageQuerySet


class CompositePageQuerySet(PageQuerySet):
    """Custom queryset which can be used by the `CompositePageManager`"""


class CompositePageManager(PageManager):
    """Custom model manager class for the `CompositePage` model."""

    def get_queryset(self) -> CompositePageQuerySet:
        return CompositePageQuerySet(model=self.model, using=self.db)
