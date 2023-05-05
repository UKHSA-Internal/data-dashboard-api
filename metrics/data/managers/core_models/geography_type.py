"""
This file contains the custom QuerySet and Manager classes associated with the `GeographyType` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models


class GeographyTypeQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `GeographyTypeManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available geography_type names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual geography_type names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<GeographyTypeQuerySet ['Nation', 'UKHSA_Region']>`

        """
        return self.all().values_list("name", flat=True).order_by("name")


class GeographyTypeManager(models.Manager):
    """Custom model manager class for the `GeographyType` model."""

    def get_queryset(self) -> GeographyTypeQuerySet:
        return GeographyTypeQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> GeographyTypeQuerySet:
        """Gets all available geography_type names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual geography_type names:
                Examples:
                    `<GeographyTypeQuerySet ['Nation', 'UKHSA_Region']>`

        """
        return self.get_queryset().get_all_names()
