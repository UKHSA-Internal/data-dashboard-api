"""
This file contains the custom QuerySet and Manager classes associated with the `Topic` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class SubThemeQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `SubThemeManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available sub_theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sub_theme names:
                Examples:
                    `<SubThemeQuerySet ['respiratory', ...]>`

        """
        return self.all().values_list("name", flat=True)


class SubThemeManager(models.Manager):
    """Custom model manager class for the `SubTheme` model."""

    def get_queryset(self) -> SubThemeQuerySet:
        return SubThemeQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> SubThemeQuerySet:
        """Gets all available sub_theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sub_theme names:
                Examples:
                    `<SubThemeQuerySet ['respiratory', ...]>`

        """
        return self.get_queryset().get_all_names()
