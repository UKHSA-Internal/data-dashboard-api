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

        logger.info(
            "Building user from JWT payload: %s",
            jwt_payload,
        )

        try:
            username = jwt_payload["entraObjectId"]
            permission_sets = jwt_payload["permissionSets"]

            logger.info("JWT payload has entraObjectId=%s", username)

            if not permission_sets:
                logger.info(
                    "Empty permissionSets in token for user: '%s'", username,
                )
                return None
        except KeyError as exc:
            logger.info(
                "Error: %s. Payload: %s", exc, jwt_payload,
            )
            return None

        user_class = get_user_model()
        user = user_class(username=username)
        user.permission_sets = permission_sets

        logger.info(
            "Permission set attached to user object"
        )

        return user
