from django.contrib.auth import get_user_model

from common.auth.cognito_jwt.user_manager import CognitoManager

USER_MODEL = get_user_model()


def test_get_or_create_for_cognito_returns_user():
    jwt_payload = {
        "entraObjectId": "unique_user_id",
        "permissionSets": ["all_the_permissions"],
    }

    user = CognitoManager.get_or_create_for_cognito(jwt_payload)
    assert user
    assert user.username == jwt_payload["entraObjectId"]
    assert user.permission_sets == jwt_payload["permissionSets"]
    assert user.is_active is True


def test_get_or_create_for_cognito_returns_none_without_username():
    jwt_payload = {
        "permissionSets": ["all_the_permissions"],
    }

    user = CognitoManager.get_or_create_for_cognito(jwt_payload)
    assert user is None


def test_get_or_create_for_cognito_returns_none_without_permission_sets():
    jwt_payload = {
        "entraObjectId": "unique_user_id",
    }

    user = CognitoManager.get_or_create_for_cognito(jwt_payload)
    assert user is None
