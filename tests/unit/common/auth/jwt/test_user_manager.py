import pytest
from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

from common.auth.jwt.user_manager import CognitoManager, EntraManager

USER_MODEL = get_user_model()


def test_get_or_create_for_cognito_returns_user():
    jwt_payload = {
        "entraObjectId": "unique_user_id",
        "permissionSets": ["all_the_permissions"],
    }

    user = CognitoManager.get_or_create(jwt_payload)
    assert user
    assert user.username == jwt_payload["entraObjectId"]
    assert user.permission_sets == jwt_payload["permissionSets"]
    assert user.is_active is True


def test_get_or_create_for_cognito_returns_none_without_username():
    jwt_payload = {
        "permissionSets": ["all_the_permissions"],
    }

    user = CognitoManager.get_or_create(jwt_payload)
    assert user is None


@patch("common.auth.jwt.user_manager.get_user_permission_set")
def test_get_or_create_for_cognito_returns_without_permission_sets(mock_get_perms):
    fake_permissions = ["Permission_1", "Permission_2"]
    mock_get_perms.return_value = fake_permissions
    jwt_payload = {
        "entraObjectId": "unique_user_id",
    }

    user = CognitoManager.get_or_create(jwt_payload)
    assert user
    assert user.username == jwt_payload["entraObjectId"]
    assert user.permission_sets == fake_permissions
    assert user.is_active is True
    mock_get_perms.assert_called_once_with(jwt_payload["entraObjectId"])


@patch("common.auth.jwt.user_manager.get_user_permission_set")
def test_get_or_create_for_cognito_returns_with_empty_permission_sets(mock_get_perms):
    fake_permissions = ["Permission_1", "Permission_2"]
    mock_get_perms.return_value = fake_permissions
    jwt_payload = {
        "entraObjectId": uuid.uuid4(),
        "permissionSets": [],
    }

    user = CognitoManager.get_or_create(jwt_payload)
    assert user
    assert user.username == jwt_payload["entraObjectId"]
    assert user.permission_sets == fake_permissions
    assert user.is_active is True
    mock_get_perms.assert_called_once_with(jwt_payload["entraObjectId"])


@patch("cms.auth_content.models.api_application.APIApplication.objects.filter")
@patch("common.auth.jwt.user_manager.get_application_permission_set")
def test_get_or_create_for_entra_returns_with_permission_sets_lookup(
    mock_get_perms, mock_api_application_filter
):
    fake_permissions = ["Permission_1", "Permission_2"]
    mock_get_perms.return_value = fake_permissions
    mock_api_application_filter.return_value.exists.return_value = True
    jwt_payload = {
        "appid": uuid.uuid4(),
    }

    user = EntraManager.get_or_create(jwt_payload, "/")
    assert user
    assert user.username == jwt_payload["appid"]
    assert user.permission_sets == fake_permissions
    assert user.is_active is True
    mock_get_perms.assert_called_once_with(jwt_payload["appid"])


@patch("common.auth.jwt.user_manager.audit_logger")
@patch("cms.auth_content.models.api_application.APIApplication.objects.filter")
@patch("common.auth.jwt.user_manager.get_application_permission_set")
def test_successful_get_or_create_for_entra_creates_audit_log(
    mock_get_perms, mock_api_application_filter, mock_audit_logger
):
    fake_permissions = ["Permission_1", "Permission_2"]
    mock_get_perms.return_value = fake_permissions
    mock_api_application_filter.return_value.exists.return_value = True
    app_id = uuid.uuid4()
    jwt_payload = {
        "appid": app_id,
    }

    user = EntraManager.get_or_create(jwt_payload, "/test-path")
    assert user
    mock_audit_logger.info.assert_called_once_with(
        "API Application auth successful",
        extra={
            "user": app_id,
            "action": "APIApplication auth successful",
            "target": "/test-path",
        },
    )


@patch("cms.auth_content.models.api_application.APIApplication.objects.filter")
def test_get_or_create_for_entra_raises_exception_if_application_not_found(
    mock_api_application_filter,
):
    mock_api_application_filter.return_value.exists.return_value = False
    jwt_payload = {
        "appid": uuid.uuid4(),
    }

    with pytest.raises(AuthenticationFailed):
        EntraManager.get_or_create(jwt_payload, "/")


def test_get_or_create_for_entra_returns_none_without_username():
    jwt_payload = {
        "permissionSets": ["all_the_permissions"],
    }

    user = EntraManager.get_or_create(jwt_payload, "/")
    assert user is None


@patch("cms.auth_content.models.api_application.APIApplication.objects.filter")
@patch("common.auth.jwt.user_manager.audit_logger")
def test_entra_rejected_appid_creates_audit_log(
    mock_audit_logger, mock_api_application_filter
):
    mock_api_application_filter.return_value.exists.return_value = False

    jwt_payload = {
        "appid": "test-app-id",
    }

    with pytest.raises(AuthenticationFailed):
        EntraManager.get_or_create(jwt_payload, "/test-path")

    mock_audit_logger.info.assert_called_once_with(
        "API Application auth rejected",
        extra={
            "user": "test-app-id",
            "action": "APIApplication auth rejected - missing or inactive",
            "target": "/test-path",
        },
    )
