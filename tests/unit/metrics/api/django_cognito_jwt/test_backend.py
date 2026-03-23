import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from utils import create_jwt_token

from metrics.api.django_cognito_jwt import backend

USER_MODEL = get_user_model()


def test_authenticate_no_token(rf):
    request = rf.get("/")
    auth = backend.JSONWebTokenAuthentication()
    assert auth.authenticate(request) is None


@pytest.mark.parametrize(
    "cognito_user_manager",
    ["metrics.api.django_cognito_jwt.user_manager.CognitoManager", None],
)
def test_authenticate_valid(
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
            f"{cognito_user_manager}.get_or_create_for_cognito", func, raising=False
        )
    else:
        monkeypatch.setattr(
            USER_MODEL.objects, "get_or_create_for_cognito", func, raising=False
        )

    request = rf.get("/", HTTP_X_UHD_AUTH=b"bearer %s" % token.encode("utf8"))
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

    request = rf.get("/", HTTP_X_UHD_AUTH=b"bearer %s" % token.encode("utf8"))
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_segments(rf):
    request = rf.get("/", HTTP_X_UHD_AUTH=b"bearer randomiets")
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_invalid_header(rf):
    request = rf.get("/", HTTP_X_UHD_AUTH=b"bearer")
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_spaces(rf):
    request = rf.get("/", HTTP_X_UHD_AUTH=b"bearer random iets")
    auth = backend.JSONWebTokenAuthentication()

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_authenticate_error_response_code():
    client = Client()
    resp = client.get("/", HTTP_X_UHD_AUTH=b"bearer random iets")

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
