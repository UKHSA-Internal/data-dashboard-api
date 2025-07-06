"""
This file contains the custom QuerySet and Manager classes associated with the `Theme` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class ThemeQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `ThemeManger`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of individual theme names:
                Examples:
                    `<ThemeQuerySet ['infectious_disease`, ...]>`
        """
        return self.all().values_list("name", flat=True)


class ThemeManager(models.Manager):
    """Custom model manager class for the `Theme` model."""

    def get_queryset(self) -> ThemeQuerySet:
        return ThemeQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> ThemeQuerySet:
        """Gets all available topic names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual theme names:
                Examples:
                    `<ThemeQuerySet ['infectious_disease', ...]>`

        """
        return self.get_queryset().get_all_names()
