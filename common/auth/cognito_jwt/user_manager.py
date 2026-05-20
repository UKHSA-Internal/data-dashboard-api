import logging
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager

from metrics.utils.permission_hierarchy import convert_permission_set_into_hierarchy

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)


class CognitoManager(BaseUserManager):

    @staticmethod
    def get_or_create_for_cognito(jwt_payload):
        """
        Create an ephemeral user instance for this request.
        We don't need to store or retrieve any info, we use what's in the JWT,
        so this speeds up the request by removing the need for any DB access
        """

        try:
            username = jwt_payload["entraObjectId"]
            raw_permission_sets = jwt_payload["permissionSets"]

            # Manual testing
            # username = "678a605b-16f3-4342-9f02-db74613701ac"
            # raw_permission_sets = {
            #     "permission_sets": [
            #         {
            #             "theme": {"id": "100", "name": "immunisation"},
            #             "sub_theme": {"id": "133", "name": "childhood-vaccines"},
            #             "topic": {"id": "-1", "name": None},
            #         }
            #     ],
            #     "summary": {"has_global_access": False},
            # }
        except KeyError:
            logger.debug(
                "Error getting entraObjectId and/or permissionSets field(s)"
                " from jwt payload: '%s'",
                jwt_payload,
            )
            return None

        permission_sets = convert_permission_set_into_hierarchy(raw_permission_sets)
        permission_count = len(permission_sets.get("permission_set_hierarchy", []))
        has_global_access = bool(permission_sets.get("has_global_access", False))

        logger.info(
            "JWT token for user '%s' with permissions: permission_count=%d, has_global_access=%s",
            username,
            permission_count,
            has_global_access,
        )

        user_class = get_user_model()
        user = user_class(username=username)
        user.permission_sets = permission_sets

        return user


def extract_jwt_permissions(*, request: "Request | None") -> dict:
    """
    Extract the normalized JWT permissions dict from an authenticated request.

    Reads `request.user.permission_sets`, which is set by CognitoManager
    during JWT authentication. Lives here because it is the counterpart to
    the code above that "writes" user.permission_sets.

    @param {Request | None} request example:
        <rest_framework.request.Request: POST '/api/charts/v3'>

    @return {dict} example:
        {
            "permission_set_hierarchy": [
                {"theme": {"id": "100", "name": "immunisation"}, ...}
            ],
            "has_global_access": False
        }
    """
    if request is None:
        return {}

    user = getattr(request, "user", None)
    if user is None:
        return {}

    permission_sets = getattr(user, "permission_sets", {})
    if not permission_sets:
        return {}

    return permission_sets
