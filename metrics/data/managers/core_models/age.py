"""
This file contains the custom QuerySet and Manager classes associated with the `Age` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models


class AgeQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `AgeManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available ages as a flat list queryset.

        Returns:
            A queryset of the individual age categories
                ordered in descending ordering starting from 0:
                Examples:
                    `<AgeQuerySet ['0-4', '10-14']>`

        """
        return self.all().values_list("name", flat=True).order_by("name")


class AgeManager(models.Manager):
    """Custom model manager class for the `Age` model."""

    def get_queryset(self) -> AgeQuerySet:
        return AgeQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> AgeQuerySet:
        """Gets all available age categories as a flat list queryset.

        Returns:
            A queryset of the individual age categories
                ordered in descending ordering starting from 0:
                Examples:
                    `<AgeQuerySet ['0-4', '10-14']>`

        """
        return self.get_queryset().get_all_names()
