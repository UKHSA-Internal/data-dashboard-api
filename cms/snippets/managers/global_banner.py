from typing import Self

from django.db import models


class GlobalBannerQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `GlobalBannerManager"""

    def get_active_banners(self) -> Self:
        """Gets the all currently active `GlobalBanner`.

        Returns:
            QuerySet: A queryset of the active banners:
                Examples:
                    `<GlobalBannerQuerySet [<GlobalBanner: Active information-level global banner>]>`
        """
        return self.filter(is_active=True)


class GlobalBannerManager(models.Manager):
    """Custom model manager class for the `GlobalBanner` model"""

    def get_queryset(self) -> GlobalBannerQuerySet:
        return GlobalBannerQuerySet(model=self.model, using=self.db)

    def get_active_banners(self):
        """Gets the currently active `GlobalBanner`.

        Returns:
            The currently active `GlobalBanner` if available.
            If there is no `GlobalBanner` with `is_active` set to True,
            then None is returned.

        """
        return self.get_queryset().get_active_banners()
