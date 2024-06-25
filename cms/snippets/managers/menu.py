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

    def is_menu_overriding_currently_active_menu(self, menu) -> bool:
        """Determines if the given `menu` is trying to override an existing active `Menu`

        Args:
            menu: The current `Menu` object which is being evaluated

        Returns:
            True if the given `menu` is trying to override
            an existing active `Menu`. False otherwise.

        """
        has_existing_active_menu: bool = self.has_active_menu()
        if not has_existing_active_menu:
            return False

        active_menu = self.get_active_menu()
        return bool(menu.is_active and menu != active_menu)
