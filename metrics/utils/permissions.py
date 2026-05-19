"""JWT-based permission validation for non-public data access."""

from typing import TypedDict


class PermissionSetLevel(TypedDict):
    """Represents a level (theme, sub_theme, or topic) in the permission hierarchy."""
    id: str
    name: str


class PermissionHierarchy(TypedDict):
    """Represents a single permission entry in the user's permission set hierarchy."""
    theme: PermissionSetLevel
    sub_theme: PermissionSetLevel
    topic: PermissionSetLevel


def check_permissions_hierarchy(
    *,
    user_permission_hierarchy: list[PermissionHierarchy] | None,
    theme_id: str,
    sub_theme_id: str,
    topic_id: str,
) -> bool:
    """
    Checks if the user's JWT permissions allow access to the requested non-public data.
    """

    if not user_permission_hierarchy:
        return False

    return check_permissions(
        user_permission_hierarchy,
        theme_id,
        sub_theme_id,
        topic_id,
    )


def check_permissions(user_permissions, theme_id, sub_theme_id, topic_id) -> bool:
    """
    TODO: This is an exact copy of cms/dashboard/viewsets.py:check_permissions(),
          which needs to be centralized!

    @return True/False whether access allowed or not
    """

    if not isinstance(user_permissions, list):
        return False

    for permission in user_permissions:
        permission_theme_id = permission.get("theme", {}).get("id")
        permission_sub_theme_id = permission.get("sub_theme", {}).get("id")
        permission_topic_id = permission.get("topic", {}).get("id")

        if permission_theme_id == "-1":
            return True

        if permission_theme_id == theme_id and permission_sub_theme_id == "-1":
            return True

        if (
                permission_theme_id == theme_id
                and permission_sub_theme_id == sub_theme_id
                and (permission_topic_id == "-1" or permission_topic_id == topic_id)
        ):
            return True

    return False
