import uuid

from django.db.models import QuerySet
from rest_framework import serializers

from auth_content.models.users import User
from metrics.utils.permission_grouping import group_by_geography, group_by_geography_type, group_by_theme
from metrics.utils.permission_hierarchy import build_permission_hierarchy, get_deduplicated_permissions


def _validate_user_id(value):
    """Validate theme_id is either wildcard or a valid integer"""
    try:
        uuid_obj = uuid.UUID(value, version=4)  # noqa: F841
    except ValueError as err:
        msg = "User ID must be a valid UUID"
        raise serializers.ValidationError(msg) from err
    else:
        return value


@staticmethod
def _validate_group_by(value):
    """Validate group_by parameter is a valid option"""
    if not value:  # Empty string or None
        return None

    valid_options = ['geography_type', 'geography', 'theme']
    if value not in valid_options:
        msg = f"Invalid group_by parameter: '{value}'. Valid options: {', '.join(valid_options)}"
        raise serializers.ValidationError(msg)

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


class UserHierarchyRequestSerializer(serializers.Serializer):
    """
    Fetches and formats user permission hierarchy with optional grouping.

    Supports different grouping strategies via 'group_by' parameter:
    - None (default): Flat deduplicated hierarchy
    - 'geography_type': Group by geography type → geography
    - 'geography': Group by specific geography
    - 'theme': Group by theme → sub-theme → topic
    """

    user_id = serializers.CharField(required=True)
    group_by = serializers.CharField(required=False, allow_blank=True)

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

    @staticmethod
    def validate_group_by(value):
        """Validate user_id is a guid"""
        return _validate_group_by(value)

    def data(self) -> dict:
        """
        Fetch user permission sets from DB and format as response.

        Returns:
            Dict with user_id and either:
            - permission_sets dict (with hierarchy and summary) if no grouping
            - permissions_by_geography_type dict if group_by='geography_type'
            - permissions_by_geography dict if group_by='geography'
            - permissions_by_theme dict if group_by='theme'

        Example (no grouping):
            {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "permission_sets": {
                    "permission_set_hierarchy": [...],
                    "summary": {...}
                }
            }

        Example (geography_type grouping):
            {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "permissions_by_geography_type": {
                    "Region": {
                        "E12000008": {
                            "geography_name": "South East",
                            "permissions": [...]
                        }
                    }
                },
                "total_permissions": 4
            }
        """

        user_id_str = self.validated_data["user_id"]
        user_uuid = uuid.UUID(user_id_str)
        group_by = self.validated_data.get("group_by")

        # Get permission sets for this user
        permission_sets = self.user_manager.get_permission_sets_for_user(
            user_uuid)

        # Check if user exists or has permissions
        if not permission_sets.exists():
            # Return empty structure rather than raising exception
            # The view can check permission_set_count and return 404 if needed
            return {
                "user_id": user_id_str,
                "permission_set_hierarchy": [],
            }

        # Convert QuerySet to list of dicts
        # permission_set_list = _queryset_to_permission_hierarchy(
        #     permission_sets)

        deduplicated_perms = get_deduplicated_permissions(permission_sets)

        if group_by == 'geography_type':
            return {
                "user_id": user_id_str,
                "permissions_by_geography_type": group_by_geography_type(deduplicated_perms),
                "total_permissions": len(deduplicated_perms),
            }

        elif group_by == 'geography':
            return {
                "user_id": user_id_str,
                "permissions_by_geography": group_by_geography(deduplicated_perms),
                "total_permissions": len(deduplicated_perms),
            }

        elif group_by == 'theme':
            return {
                "user_id": user_id_str,
                "permissions_by_theme": group_by_theme(deduplicated_perms),
                "total_permissions": len(deduplicated_perms),
            }

        else:
            # Default: Return flat deduplicated hierarchy with summary
            hierarchy = _queryset_to_permission_hierarchy(permission_sets)
            return {
                "user_id": user_id_str,
                "permission_sets": hierarchy,
            }


class UserPermissionSetResponseSerializer(serializers.Serializer):
    """Formats the response for choice endpoints"""

    user_id = serializers.CharField(help_text="UUID of the user")

    permission_sets = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of permission set objects assigned to the user",
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


def _queryset_to_permission_hierarchy(queryset: QuerySet) -> dict:
    """
    Convert a PermissionSet QuerySet to a deduplicated permission hierarchy.

    This uses subsumption logic to remove overlapping permissions without
    needing to query for all child items in the database.

    Args:
        queryset: QuerySet of PermissionSet objects

    Returns:
        Dict containing permission_set_hierarchy list and summary

    Examples:
        >>> qs = PermissionSet.objects.filter(user__user_id=some_uuid)
        >>> _queryset_to_permission_hierarchy(qs)
        {
            'permission_set_hierarchy': [
                {
                    'theme': {'id': '2', 'name': 'infectious_disease'},
                    'sub_theme': {'id': '2', 'name': 'respiratory'},
                    'topic': {'id': '3', 'name': 'COVID-19'},
                    'metric': {'id': '-1', 'name': '* (All)'},
                    'geography_type': {'id': '-1', 'name': '* (All)'},
                    'geography': {'id': '-1', 'name': '* (All)'}
                }
            ],
            'summary': {
                'total_permission_sets': 2,
                'deduplicated_count': 1,
                'removed_count': 1,
                'has_global_access': False,
                'wildcard_themes': [],
                'wildcard_geography_types': ['* (All)']
            }
        }
    """

    return build_permission_hierarchy(queryset)
