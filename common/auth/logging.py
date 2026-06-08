"""Utilities for logging authentication and permission information across the API."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def log_user_permissions(user: Any) -> None:
    """Log permission information for an authenticated user.

    This function logs the permission set summary and global access status,
    consistent with the CMS dashboard viewset logging.

    Args:
        user: The authenticated user object that comes with a user.permission_sets.
    """

    if not hasattr(user, "permission_sets"):
        return

    permission_sets = user.permission_sets

    if isinstance(permission_sets, dict):
        summary = permission_sets.get("summary", {})
        total_permission_sets = summary.get("total_permission_sets", "unknown")
        has_global_access = summary.get("has_global_access", False)
    elif isinstance(permission_sets, list | tuple):
        if not permission_sets:
            return

        total_permission_sets = len(permission_sets)
        has_global_access = any(
            isinstance(permission_set, dict)
            and permission_set.get("theme", {}).get("id") == "-1"
            and permission_set.get("geography_type", {}).get("id") == "-1"
            for permission_set in permission_sets
        )
    else:
        return

    logger.info(
        "User %s has total permission sets: %s",
        user.username,
        total_permission_sets,
    )

    logger.info(
        "User %s has global access: %s",
        user.username,
        has_global_access,
    )
