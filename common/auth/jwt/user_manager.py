import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager

from metrics.data.managers.rbac_models.user import UserManager
from cms.auth_content.models.users import User
from metrics.utils.permission_hierarchy import build_permission_hierarchy
from rest_framework import exceptions

logger = logging.getLogger(__name__)


def get_user_permission_set(id: str):
    permissions = UserManager.get_permission_sets_for_user(id)
    return build_permission_hierarchy(permissions)


class CognitoManager(BaseUserManager):

    @staticmethod
    def get_or_create(jwt_payload):
        """Create an ephemeral user instance for this request.
        If the permissions aren't present in the JWT, queries for them in
        the database based on the entraObjectId in the token
        """
        try:
            username = jwt_payload["entraObjectId"]
            # Check if the JWT already includes permissionSets
            # Use if found, if not grab user permissions from the database
            if "permissionSets" in jwt_payload:
                permission_sets = jwt_payload["permissionSets"]
            else:
                permission_sets = get_user_permission_set(username)
        except KeyError:
            logger.debug(
                "Error getting entraObjectId and/or permissionSets field(s)"
                " from jwt payload: '%s'",
                jwt_payload,
            )
            return None

        user_class = get_user_model()
        user = user_class(username=username)
        user.permission_sets = permission_sets
        return user


class EntraManager(BaseUserManager):

    @staticmethod
    def get_or_create(jwt_payload):
        """Create an ephemeral user instance for this request.
        If the provided appid isn't present in the database, raises
        AuthenticationFailed exception
        """
        try:
            username = jwt_payload["appid"]
            if not User.objects.filter(user_id=username).exists():
                raise exceptions.AuthenticationFailed(("Application not found."))
            permission_sets = get_user_permission_set(username)
        except KeyError:
            logger.info(
                "Error getting entraObjectId and/or permissionSets field(s)"
                " from jwt payload: '%s'",
                jwt_payload,
            )
            return None

        user_class = get_user_model()
        user = user_class(username=username)
        user.permission_sets = permission_sets
        return user
