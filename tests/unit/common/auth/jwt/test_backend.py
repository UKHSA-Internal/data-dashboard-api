import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, override_settings
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from unittest.mock import patch
from utils import create_jwt_token
import uuid

from common.auth.jwt import backend

USER_MODEL = get_user_model()


def test_get_authorization_header(rf):
    """test get_authorization_header correctly handles
    a header that is a string not a bytestring as expected"""
    headers = {settings.JWT_AUTH_HEADER: "bearer string_token"}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


@override_settings()
def test_get_auth_header_no_value(rf):
    """test get_authorization_header finds no token header if
    JWT_AUTH_HEADER is set to None"""
    settings.JWT_AUTH_HEADER = None
    headers = {"HTTP_AUTHORIZATION": b"bearer string token"}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    assert auth.authenticate(request) is None


@override_settings()
def test_get_default_auth_header(rf):
    """test get_authorization_header uses 'Authorization' header if
    JWT_AUTH_HEADER is not specified in settings"""
    del settings.JWT_AUTH_HEADER
    # Prepend `HTTP_` as it's normally done by Django
    headers = {"HTTP_AUTHORIZATION": b"bearer string token"}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_no_token(rf):
    request = rf.get("/")
    auth = backend.JSONWebTokenAuthentication()
    assert auth.authenticate(request) is None


@pytest.mark.parametrize(
    "cognito_user_manager",
    ["common.auth.jwt.user_manager.CognitoManager", None],
)
def test_custom_user_manager_cognito(
    rf, monkeypatch, cognito_well_known_keys, jwk_private_key_one, cognito_user_manager
):
    settings.COGNITO_USER_MANAGER = cognito_user_manager
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": settings.COGNITO_AUDIENCE,
            "sub": "username",
            "entraObjectId": "entraOID",
        },
    )

    @staticmethod
    def func(payload):
        return USER_MODEL(username=payload["entraObjectId"])

    if cognito_user_manager:
        monkeypatch.setattr(
            f"{cognito_user_manager}.get_or_create", func, raising=False
        )
    else:
        monkeypatch.setattr(USER_MODEL.objects, "get_or_create", func, raising=False)

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    user, auth_token = auth.authenticate(request)
    assert user
    assert user.username == "entraOID"
    assert auth_token == token.encode("utf8")


def test_authenticate_valid_token_with_permission_set(
    rf, cognito_well_known_keys, jwk_private_key_one
):
    settings.COGNITO_USER_MANAGER = "common.auth.jwt.user_manager.CognitoManager"
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": settings.COGNITO_AUDIENCE,
            "sub": "username",
            "entraObjectId": "entraOID",
            "permissionSets": ["something"],
        },
    )

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    user, auth_token = auth.authenticate(request)
    assert user
    assert user.username == "entraOID"
    assert auth_token == token.encode("utf8")


@patch("common.auth.jwt.user_manager.get_user_permission_set")
def test_authenticate_valid_token_without_permission_set(
    mock_get_perms, rf, cognito_well_known_keys, jwk_private_key_one
):
    fake_permissions = ["Permission_1", "Permission_2"]
    mock_get_perms.return_value = fake_permissions

    settings.COGNITO_USER_MANAGER = "common.auth.jwt.user_manager.CognitoManager"
    entra_id = str(uuid.uuid4())
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": settings.COGNITO_AUDIENCE,
            "sub": "username",
            "entraObjectId": entra_id,
        },
    )

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    user, auth_token = auth.authenticate(request)
    assert user
    assert user.username == entra_id
    assert auth_token == token.encode("utf8")
    mock_get_perms.assert_called_once_with(entra_id)


def test_authenticate_valid_token_with_empty_permission_set(
    rf, cognito_well_known_keys, jwk_private_key_one
):
    settings.COGNITO_USER_MANAGER = "common.auth.jwt.user_manager.CognitoManager"
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": settings.COGNITO_AUDIENCE,
            "sub": "username",
            "entraObjectId": "entraOID",
            "permissionSets": [],
        },
    )

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    user, auth_token = auth.authenticate(request)
    assert user
    assert user.username == "entraOID"
    assert auth_token == token.encode("utf8")


def test_authenticate_invalid(rf, cognito_well_known_keys, jwk_private_key_two):
    token = create_jwt_token(
        jwk_private_key_two,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": settings.COGNITO_AUDIENCE,
            "sub": "username",
        },
    )

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_segments(rf):
    headers = {settings.JWT_AUTH_HEADER: b"bearer randomiets"}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_invalid_header(rf):
    headers = {settings.JWT_AUTH_HEADER: b"bearer"}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_spaces(rf):
    headers = {settings.JWT_AUTH_HEADER: b"bearer random iets"}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_response_code():
    client = Client()
    headers = {settings.JWT_AUTH_HEADER: b"bearer random iets"}
    resp = client.get("/", **headers)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticate_invalid_entra(rf, entra_well_known_keys, jwk_private_key_two):
    token = create_jwt_token(
        jwk_private_key_two,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
        },
    )

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


@pytest.mark.parametrize(
    "entra_user_manager",
    ["common.auth.jwt.user_manager.EntraManager", None],
)
def test_custom_user_manager_entra(
    rf, monkeypatch, entra_well_known_keys, jwk_private_key_one, entra_user_manager
):
    settings.ENTRA_USER_MANAGER = entra_user_manager
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "aud": settings.ENTRA_AUDIENCE,
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
        },
    )

    @staticmethod
    def func(payload):
        return USER_MODEL(username=payload["appid"])

    if entra_user_manager:
        monkeypatch.setattr(f"{entra_user_manager}.get_or_create", func, raising=False)
    else:
        monkeypatch.setattr(USER_MODEL.objects, "get_or_create", func, raising=False)

    headers = {settings.JWT_AUTH_HEADER: b"bearer %s" % token.encode("utf8")}
    request = rf.get("/", **headers)
    auth = backend.JSONWebTokenAuthentication()
    user, auth_token = auth.authenticate(request)
    assert user
    assert user.username == "entraOID"
    assert auth_token == token.encode("utf8")
