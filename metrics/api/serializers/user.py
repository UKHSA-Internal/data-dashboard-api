from django.db.models import QuerySet
from rest_framework import serializers
import uuid

from auth_content.models.users import User


def _validate_user_id(value):
    """Validate theme_id is either wildcard or a valid integer"""
    try:
        uuid_obj = uuid.UUID(value, version=4)
    except ValueError as err:
        msg = "User ID must be a valid UUID"
        raise serializers.ValidationError(msg) from err
    else:
        return value


class UserRequestSerializer(serializers.Serializer):
    """Fetches and formats sub-theme choices based on theme_id"""

    user_id = serializers.CharField(required=True)

    @property
    def user_manager(self):
        """
        Fetch the topic manager from the context if available.
        If not get the Manager which has been declared on the `Topic` model.
        """
        return self.context.get("user_manager", User.objects)

    @staticmethod
    def validate_user_id(value):
        """Validate user_id is a guid"""
        return _validate_user_id(value)

    def data(self) -> dict:
        """
        Fetch user permission sets from DB and format as response.

        Returns:
            Dict with user_id, permission_sets list, and count

        Example:
            {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "permission_sets": [
                    {
                        "id": 1,
                        "name": "Theme: Infectious Disease | ...",
                        "theme": "1",
                        "sub_theme": "3",
                        ...
                    }
                ],
                "permission_set_count": 1
            }
        """
        user_id_str = self.validated_data["user_id"]
        user_uuid = uuid.UUID(user_id_str)

        # Get permission sets for this user
        permission_sets = self.user_manager.get_permission_sets_for_user(
            user_uuid)

        # Check if user exists or has permissions
        if not permission_sets.exists():
            # Return empty structure rather than raising exception
            # The view can check permission_set_count and return 404 if needed
            return {
                "user_id": user_id_str,
                "permission_sets": [],
                "permission_set_count": 0,
            }

        # Convert QuerySet to list of dicts
        permission_set_list = _queryset_to_permission_set_dicts(
            permission_sets)

        return {
            "user_id": user_id_str,
            "permission_sets": permission_set_list,
            "permission_set_count": len(permission_set_list),
        }


class UserPermissionSetResponseSerializer(serializers.Serializer):
    """Formats the response for choice endpoints"""

    user_id = serializers.CharField(
        help_text="UUID of the user"
    )

    permission_sets = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of permission set objects assigned to the user"
    )

    permission_set_count = serializers.IntegerField(
        help_text="Total number of permission sets assigned to the user"
    )


def _queryset_to_permission_set_dicts(
    queryset: QuerySet,
) -> list[dict]:
    """
    Convert a PermissionSet QuerySet to a list of dictionaries.

    Args:
        queryset: QuerySet of PermissionSet objects

    Returns:
        List of dictionaries containing permission set data

    Examples:
        >>> qs = PermissionSet.objects.filter(user__user_id=some_uuid)
        >>> _queryset_to_permission_set_dicts(qs)
        [
            {
                'id': 1,
                'name': 'Theme: Infectious Disease | ...',
                'theme': '1',
                'sub_theme': '3',
                'topic': '5',
                'metric': '10',
                'geography_type': 'Nation',
                'geography': 'E92000001'
            },
            ...
        ]
    """
    return list(
        queryset.values(
            "id",
            "name",
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography_type",
            "geography",
        )
    )
