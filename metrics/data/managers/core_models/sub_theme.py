"""
This file contains the custom QuerySet and Manager classes associated with the `Topic` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class SubThemeQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `SubThemeManager`"""

    def get_name_by_id(self, sub_theme_id: int) -> str | None:
        """
        Gets the sub_theme name which matches the given sub_theme id.

        Args:
            sub_theme_id: The ID of the theme to look up

        Returns:
            The sub_theme name if found, None otherwise

        Examples:
            >>> SubThemeQuerySet.get_name_by_id(1)
            'respiratory'
            >>> SubThemeQuerySet.get_name_by_id(999)
            None
        """
        return self.filter(id=sub_theme_id).values_list("name", flat=True).first()

    def get_all_names(self) -> models.QuerySet:
        """Gets all available sub_theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sub_theme names:
                Examples:
                    `<SubThemeQuerySet ['respiratory', ...]>`

        """
        return self.all().values_list("name", flat=True)

    def get_all_unique_names(self) -> models.QuerySet:
        """Gets all available unique sub_theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual unique sub_theme names:
            ordered in descending order from A -> Z:
            Examples:
                `<SubThemeQuerySet ['respiratory', ...]>`
        """
        return self.all().values_list("name", flat=True).distinct().order_by("name")

    def get_all_names_and_ids(self) -> models.QuerySet:
        """Gets all available sub_themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.all().values("id", "name").distinct()

    def get_filtered_unique_names_related_to_theme(
        self, parent_theme_id
    ) -> models.QuerySet:
        """Gets all available unique sub_themes with id and name fields that are related to the parent theme ID.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.filter(theme_id=parent_theme_id).values("id", "name").distinct()


class SubThemeManager(models.Manager):
    """Custom model manager class for the `SubTheme` model."""

    def get_queryset(self) -> SubThemeQuerySet:
        return SubThemeQuerySet(model=self.model, using=self.db)

    def get_name_by_id(self, sub_theme_id: int) -> str | None:
        """Gets the sub_theme name which matches the given sub_theme id.

        Args:
            sub_theme_id: The ID of the theme to look up

        Returns:
            The sub_theme name if found, None otherwise

        Examples:
            >>> SubThemeManager.get_name_by_id(1)
            'respiratory'
            >>> SubThemeManager.get_name_by_id(999)
            None
        """
        return self.get_queryset().get_name_by_id(sub_theme_id)

    def get_all_names(self) -> SubThemeQuerySet:
        """Gets all available sub_theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual sub_theme names:
                Examples:
                    `<SubThemeQuerySet ['respiratory', ...]>`

        """
        return self.get_queryset().get_all_names()

    def get_all_unique_names(self) -> SubThemeQuerySet:
        """Gets all available unique sub_theme names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual unique sub_theme names:
            ordered in descending order from A -> Z:
            Examples:
                `<SubThemeQuerySet ['respiratory', ...]>`
        """
        return self.get_queryset().get_all_unique_names()

    def get_filtered_unique_names_related_to_theme(
        self, parent_theme_id: str
    ) -> SubThemeQuerySet:
        """Gets all available sub_themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.get_queryset().get_filtered_unique_names_related_to_theme(
            parent_theme_id=parent_theme_id
        )

    def get_all_names_and_ids(self) -> SubThemeQuerySet:
        """Gets all available sub_themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<SubThemeQuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.get_queryset().get_all_names_and_ids()
