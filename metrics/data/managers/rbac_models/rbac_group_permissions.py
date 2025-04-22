from typing import Union

from django.db import models


class RBACGroupPermissionQuerySet(models.QuerySet):
    """Custom queryset for the `RBACGroupPermission` model."""

    def get_group(self, group_id: str) -> Union["RBACGroupPermission", None]:
        """
        Retrieves a single `RBACGroupPermission` instance based on the given name.

        Since the `name` field has a unique constraint, this method returns at most one group.

        Args:
            group_id (str): The group ID unique identifier associated with the group permission.

        Returns:
            RBACGroupPermission | None: The matching group permission instance if found, otherwise None.
        """
        return self.filter(group_id=group_id).first()


class RBACGroupPermissionManager(models.Manager):
    """Custom manager for the `RBACGroupPermission` model."""

    def get_queryset(self) -> RBACGroupPermissionQuerySet:
        """
        Returns the custom queryset for RBACGroupPermission.

        This allows access to custom queryset methods.
        """
        return RBACGroupPermissionQuerySet(self.model, using=self._db)

    def get_group(self, group_id: str) -> Union["RBACGroupPermission", None]:
        """
        Retrieves a single `RBACGroupPermission` instance by the group ID

        Args:
            group_id (str): The group ID unique identifier associated with the group permission.

        Returns:
            RBACGroupPermission | None: The matching group permission instance if found, otherwise None.
        """
        return self.get_queryset().get_group(group_id)
