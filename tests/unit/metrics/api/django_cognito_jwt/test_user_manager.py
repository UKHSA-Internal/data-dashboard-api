from unittest import mock
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from metrics.api.django_cognito_jwt.user_manager import CognitoManager

USER_MODEL = get_user_model()


def test_get_or_create_for_cognito_get_existing_user():
    jwt_payload = {
        "entraObjectId": "unique_user_id",
    }

    mock_user = mock.MagicMock()
    mock_user.username = jwt_payload["entraObjectId"]
    mock_user.is_active = True

    with mock.patch.object(USER_MODEL.objects, "get", return_value=mock_user):
        user = CognitoManager.get_or_create_for_cognito(jwt_payload)
        assert user
        assert user.username == jwt_payload["entraObjectId"]
        assert user.is_active is True


def test_get_or_create_for_cognito_create_user():
    jwt_payload = {
        "entraObjectId": "unique_user_id",
    }

    def create_user_mock(*args, username, **kwargs):
        mock_user = mock.MagicMock()
        mock_user.username = username
        return mock_user

    with (
        mock.patch.object(USER_MODEL.objects, "get", side_effect=User.DoesNotExist),
        mock.patch.object(
            USER_MODEL.objects, "create_user", side_effect=create_user_mock
        ) as create_user,
    ):
        user = CognitoManager.get_or_create_for_cognito(jwt_payload)
        assert user
        assert user.username == jwt_payload["entraObjectId"]
        assert user.is_active is True

        create_user.assert_called_once_with(
            username=jwt_payload["entraObjectId"],
            password=None,
        )
