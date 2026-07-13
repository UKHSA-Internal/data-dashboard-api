import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from rest_framework import exceptions

from cms.auth_content.models.api_application import APIApplication
from cms.auth_content.models.permission_sets import PermissionSet
from metrics.data.managers.rbac_models.user import UserManager
from metrics.utils.permission_hierarchy import build_permission_hierarchy

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")


def get_user_permission_set(user_id: str):
    permissions = UserManager.get_permission_sets_for_user(user_id)
    return build_permission_hierarchy(permissions)


def get_application_permission_set(app_id: str):
    permissions = PermissionSet.objects.filter(apiapplication__application_id=app_id)
    return build_permission_hierarchy(permissions)


class CognitoManager(BaseUserManager):

    @staticmethod
    def get_or_create(jwt_payload, request_path=None):
        """Create an ephemeral user instance for this request.
        If the permissions aren't present in the JWT, queries for them in
        the database based on the entraObjectId in the token
        """
        try:
            username = jwt_payload["entraObjectId"]
            # Check if the JWT already includes permissionSets
            # Use if found, if not grab user permissions from the database
            if "permissionSets" in jwt_payload and jwt_payload["permissionSets"] != []:
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
    def get_or_create(jwt_payload, request_path):
        """Create an ephemeral user instance for this request.
        If the provided appid isn't present in the database, raises
        AuthenticationFailed exception
        """
        try:
            username = jwt_payload["appid"]

            if not APIApplication.objects.filter(
                application_id=username, is_active=True
            ).exists():
                audit_logger.info(
                    "API Application auth rejected",
                    extra={
                        "user": username,
                        "action": "APIApplication auth rejected - missing or inactive",
                        "target": request_path,
                    },
                )
                msg = "Application not found."
                raise exceptions.AuthenticationFailed(msg)

        except KeyError:
            logger.info(
                "Error getting appid field from jwt payload: '%s'",
                jwt_payload,
            )
            return None

        permission_sets = get_application_permission_set(username)

        user_class = get_user_model()
        user = user_class(username=username)
        user.permission_sets = permission_sets
        audit_logger.info(
            "API Application auth successful",
            extra={
                "user": username,
                "action": "APIApplication auth successful",
                "target": request_path,
            },
        )
        return user
