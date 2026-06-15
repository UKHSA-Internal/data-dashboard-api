"""Utilities for logging authentication and permission information across the API."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def log_user_permission_summary(user: Any) -> None:
    """Log permission information for an authenticated user.

    This function logs the permission set summary and global access status.
    It expects ``user.permission_sets`` to be a dict with the shape produced
    by ``CognitoManager.get_or_create_for_cognito``:

    .. code-block:: python

        {
            "permission_sets": [...],
            "summary": {"total_permission_sets": 2, "has_global_access": False},
        }

    Args:
        user: The authenticated user object that has a ``permission_sets`` dict.
    """

    if not hasattr(user, "username"):
        return
    if not hasattr(user, "permission_sets"):
        return

    username = user.username
    permission_sets = user.permission_sets

    if not isinstance(permission_sets, dict):
        return

    log_msg = f'User {username} has total permission sets {permission_sets["summary"]["total_permission_sets"]}'

    if permission_sets["summary"]["has_global_access"]:
        log_msg += " and global access"

    logger.info(log_msg)
