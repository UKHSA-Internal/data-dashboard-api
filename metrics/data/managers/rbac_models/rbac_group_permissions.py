from django.db import models


class RBACGroupPermissionQuerySet(models.QuerySet):
    """Custom queryset for the `RBACGroupPermission` model."""

    def get_group(self, name: str) -> "RBACGroupPermission":
        """
        Retrieves a single `RBACGroupPermission` instance based on the given name.

        Since the `name` field has a unique constraint, this method returns at most one group.

        Args:
            name (str): The name of the group permission to retrieve.

        Returns:
            RBACGroupPermission | None: The matching group permission instance if found, otherwise None.
        """
        return self.filter(name=name).first()


class RBACGroupPermissionManager(models.Manager):
    """Custom manager for the `RBACGroupPermission` model."""

    def get_queryset(self) -> RBACGroupPermissionQuerySet:
        """
        Returns the custom queryset for RBACGroupPermission.

        This allows access to custom queryset methods like `get_group()`.
        """
        return RBACGroupPermissionQuerySet(self.model, using=self._db)

    def get_group(self, name: str) -> "RBACGroupPermission":
        """
        Retrieves a single `RBACGroupPermission` instance by name using the queryset method.

        Args:
            name (str): The name of the group permission to retrieve.

        Returns:
            RBACGroupPermission | None: The matching group permission instance if found, otherwise None.
        """
        return self.get_queryset().get_group(name)
