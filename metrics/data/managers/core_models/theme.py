"""
This file contains the custom QuerySet and Manager classes associated with the `Theme` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class ThemeQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `ThemeManger`"""

    def get_name_by_id(self, theme_id: int) -> str | None:
        """
        Gets the theme name which matches the given theme id.

        Args:
            theme_id: The ID of the theme to look up

        Returns:
            The theme name if found, None otherwise

        Examples:
            >>> ThemeQuerySet.get_name_by_id(1)
            'infectious_disease'
            >>> ThemeQuerySet.get_name_by_id(999)
            None
        """
        return self.filter(id=theme_id).values_list("name", flat=True).first()
        

    def get_all_names(self) -> models.QuerySet:
        """Gets all available theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of individual theme names:
                Examples:
                    `<ThemeQuerySet ['infectious_disease`, ...]>`
        """
        return self.all().values_list("name", flat=True)

    def get_all_names_and_ids(self) -> models.QuerySet:
        """Gets all available themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.all().values("id", "name")


class ThemeManager(models.Manager):
    """Custom model manager class for the `Theme` model."""

    def get_queryset(self) -> ThemeQuerySet:
        return ThemeQuerySet(model=self.model, using=self.db)

    def get_name_by_id(self, theme_id: int) -> str | None:
        """Gets the theme name which matches the given theme id.

        Args:
            theme_id: The ID of the theme to look up

        Returns:
            The theme name if found, None otherwise

        Examples:
            >>> ThemeManager.get_name_by_id(1)
            'infectious_disease'
            >>> ThemeManager.get_name_by_id(999)
            None
        """
        return self.get_queryset().get_name_by_id(theme_id)

    def get_all_names(self) -> ThemeQuerySet:
        """Gets all available topic names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual theme names:
                Examples:
                    `<ThemeQuerySet ['infectious_disease', ...]>`

        """
        return self.get_queryset().get_all_names()

    def get_all_names_and_ids(self) -> ThemeQuerySet:
        """Gets all available themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<ThemeQuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.get_queryset().get_all_names_and_ids()
