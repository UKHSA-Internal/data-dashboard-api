import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager

logger = logging.getLogger(__name__)


class CognitoManager(BaseUserManager):

    @staticmethod
    def get_or_create_for_cognito(jwt_payload):
        """Create an ephemeral user instance for this request.
        We don't need to store or retrieve any info, we use what's in the JWT,
        so this speeds up the request by removing the need for any DB access
        """
        try:
            username = jwt_payload["entraObjectId"]
            permission_sets = jwt_payload["permissionSets"]

            # DEBUGGING: Manual testing (just for now)
            # username = "{YOUR_ENTRA_OBJECT_ID}"
            # permission_sets = {
            #     "permission_sets": [
            #         {
            #             "theme": {"id": "100", "name": "immunisation"},
            #             "sub_theme": {"id": "133", "name": "childhood-vaccines"},
            #             "topic": {"id": "-1", "name": "* (All)"},
            #             "metric": {"id": "-1", "name": "* (All)"},
            #             "geography_type": {"id": "-1", "name": "* (All)"},
            #             "geography": {"id": "-1", "name": "* (All)"},
            #         }
            #     ],
            #     "summary": {"has_global_access": False},
            # }

            if not permission_sets:
                logger.debug(
                    "Empty permissionSets in token for user: '%s'",
                    username,
                )
                return None
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
