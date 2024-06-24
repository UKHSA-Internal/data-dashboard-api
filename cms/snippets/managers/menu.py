from typing import Self

from django.db import models


class MenuQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `MenuManager"""

    def get_active_menus(self) -> Self:
        """Gets the all currently active `Menu`.

        Returns:
            QuerySet: A queryset of the active banners:
                Examples:
                    `<MenuQuerySet [<Menu>]>`
        """
        return self.filter(is_active=True)


class MenuManager(models.Manager):
    """Custom model manager class for the `Menu` model"""

    def get_queryset(self) -> MenuQuerySet:
        return MenuQuerySet(model=self.model, using=self.db)

    def has_active_menu(self) -> bool:
        """Checks if there is already a `Menu` which is active

        Returns:
            True if there is a `Menu` which has `is_active` set to True.
            False otherwise.

        """
        return self.get_queryset().get_active_menus().exists()

    def get_active_menu(self):
        """Gets the currently active `Menu`.

        Returns:
            The currently active `Menu` if available.
            If there is no `Menu` with `is_active` set to True,
            then None is returned.

        """
        return self.get_queryset().get_active_menus().first()
