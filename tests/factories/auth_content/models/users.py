import factory

from cms.auth_content.models.permission_sets import PermissionSet
from cms.auth_content.models.users import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `User` instances for tests
    """

    class Meta:
        model = User

    @classmethod
    def create_with_permission_set(cls, user_id: str, permission_set_name: str):
        """
        Create a user with a single permission set.

        Args:
            user_id: UUID for the user
            permission_set_name: Name of the permission set to assign

        Returns:
            User instance with permission set assigned
        """
        permission_set, _ = PermissionSet.objects.get_or_create(
            name=permission_set_name
        )

        # Create user first
        user = cls.create(user_id=user_id)

        # Then add the permission set using .add()
        user.permission_sets.add(permission_set)

        return user

    @classmethod
    def create_with_permission_sets(cls, user_id: str, permission_sets: list):
        """
        Create a user with multiple permission sets.

        Args:
            user_id: UUID for the user
            permission_sets: List of PermissionSet instances

        Returns:
            User instance with permission sets assigned
        """
        user = cls.create(user_id=user_id)
        user.permission_sets.set(permission_sets)
        return user
