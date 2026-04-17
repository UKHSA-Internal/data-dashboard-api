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
        except KeyError:
            logger.exception(
                "Error getting entraObjectId and permissionSets from jwt '%s'",
                jwt_payload,
            )
            return None

        user_class = get_user_model()
        user = user_class(username=username)
        user.permission_sets = permission_sets
        return user
