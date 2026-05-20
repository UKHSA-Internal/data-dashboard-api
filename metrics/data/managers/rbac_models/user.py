"""
Custom QuerySet and Manager classes for the User model.

The application layer should only call into the Manager class.
The application should not interact directly with the QuerySet class.
"""

from uuid import UUID

from django.db import models

from cms.auth_content.models.permission_sets import PermissionSet


class UserQuerySet(models.QuerySet):
    """Custom queryset for User model operations."""

    def get_user_with_permission_sets(self, user_id: UUID) -> models.QuerySet:
        """
        Get user with their permission sets prefetched.

        Args:
            user_id: UUID of the user

        Returns:
            QuerySet containing the user with permission_sets prefetched

        Examples:
            >>> user = User.objects.get_user_with_permission_sets(uuid_value).first()
            >>> user.permission_sets.all()
            <QuerySet [<PermissionSet: ...>, ...]>
        """
        return self.filter(user_id=user_id).prefetch_related("permission_sets")


class UserManager(models.Manager):
    """Custom model manager class for the User model."""

    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(model=self.model, using=self.db)

    def get_user_with_permission_sets(self, user_id: UUID) -> UserQuerySet:
        """
        Get user with their permission sets prefetched.

        This efficiently loads the user and all their related permission sets
        in a minimal number of database queries.

        Args:
            user_id: UUID of the user

        Returns:
            QuerySet containing the user with permission_sets prefetched

        Examples:
            >>> user = User.objects.get_user_with_permission_sets(some_uuid).first()
            >>> for perm in user.permission_sets.all():
            ...     print(perm.name)
        """
        return self.get_queryset().get_user_with_permission_sets(user_id=user_id)

    @staticmethod
    def get_permission_sets_for_user(user_id: UUID) -> models.QuerySet:
        """
        Get all permission sets for a user directly.

        This bypasses the User object and returns the permission sets directly,
        which is useful for the API endpoints.

        Args:
            user_id: UUID of the user

        Returns:
            QuerySet of PermissionSet objects assigned to the user

        Examples:
            >>> perms = User.objects.get_permission_sets_for_user(some_uuid)
            >>> perms.count()
            5
        """
        return PermissionSet.objects.filter(user__user_id=user_id)
