import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager, User

logger = logging.getLogger(__name__)


class CognitoManager(BaseUserManager):

    @staticmethod
    def get_or_create_for_cognito(jwt_payload):
        username = jwt_payload["entraObjectId"]
        try:
            user = get_user_model().objects.get(username=username)
            logger.debug("Found existing user %s", user.username)
        except User.DoesNotExist:
            password = None
            user = get_user_model().objects.create_user(
                username=username,
                password=password,
            )
            logger.info("Created user %s", user.username)
            user.is_active = True
            user.save()
        return user
