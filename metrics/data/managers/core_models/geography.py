"""
This file contains the custom QuerySet and Manager classes associated with the `Geography` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class GeographyQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `GeographyManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available geography names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual geography names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<GeographyQuerySet ['England', 'London']>`

        """
        return self.all().values_list("name", flat=True).distinct().order_by("name")


class GeographyManager(models.Manager):
    """Custom model manager class for the `Geography` model."""

    def get_queryset(self) -> GeographyQuerySet:
        return GeographyQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> GeographyQuerySet:
        """Gets all available deduplicated geography names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual geography names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<GeographyQuerySet ['England', 'London']>`

        """
        return self.get_queryset().get_all_names()
