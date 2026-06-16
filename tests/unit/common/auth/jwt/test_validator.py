import pytest
from datetime import datetime, timedelta, timezone
from django.conf import settings
from utils import create_jwt_token

from common.auth.jwt import validator


def test_validate_token(cognito_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": "my-audience",
            "sub": "username",
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    auth.validate(token)


def test_validate_token_error_key(cognito_well_known_keys, jwk_private_key_two):
    token = create_jwt_token(
        jwk_private_key_two,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": "my-audience",
            "sub": "username",
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    with pytest.raises(validator.TokenError):
        auth.validate(token)


def test_validate_token_valid_expiry(cognito_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": "my-audience",
            "sub": "username",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15),
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    auth.validate(token)


def test_validate_token_error_expired(cognito_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": "my-audience",
            "sub": "username",
            "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=15),
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    with pytest.raises(validator.TokenError):
        auth.validate(token)


def test_validate_token_error_aud(cognito_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": "other-audience",
            "sub": "username",
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")

    with pytest.raises(validator.TokenError):
        auth.validate(token)


def test_validate_token_missing_aud(cognito_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            # missing aud
            "sub": "username",
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    auth.validate(token)


@pytest.mark.parametrize(
    "is_cache_enabled,responses_calls", [(None, 2), (False, 2), (True, 1)]
)
def test_validate_token_caching(
    cognito_well_known_keys,
    jwk_private_key_one,
    settings,
    responses,
    is_cache_enabled,
    responses_calls,
):
    if is_cache_enabled is not None:
        settings.COGNITO_PUBLIC_KEYS_CACHING_ENABLED = is_cache_enabled

    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": "https://cognito-idp.eu-central-1.amazonaws.com/bla",
            "aud": "my-audience",
            "sub": "username",
        },
    )
    auth = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    auth.validate(token)
    assert len(responses.calls) == 1

    auth_again = validator.CognitoTokenValidator("eu-central-1", "bla", "my-audience")
    auth_again.validate(token)
    assert len(responses.calls) == responses_calls


def test_validate_entra_token(entra_well_known_keys, jwk_private_key_one):
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
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    auth.validate(token)


def test_validate_token_error_key_entra(entra_well_known_keys, jwk_private_key_two):
    token = create_jwt_token(
        jwk_private_key_two,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "aud": settings.ENTRA_AUDIENCE,
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
        },
    )
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    with pytest.raises(validator.TokenError):
        auth.validate(token)


def test_validate_token_valid_expiry_entra(entra_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "aud": settings.ENTRA_AUDIENCE,
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15),
        },
    )
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    auth.validate(token)


def test_validate_token_error_expired_entra(entra_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "aud": settings.ENTRA_AUDIENCE,
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
            "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=15),
        },
    )
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    with pytest.raises(validator.TokenError):
        auth.validate(token)


def test_validate_token_error_aud_entra(entra_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "aud": "other-aud",
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
        },
    )
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )

    with pytest.raises(validator.TokenError):
        auth.validate(token)


def test_validate_token_missing_aud_entra(entra_well_known_keys, jwk_private_key_one):
    token = create_jwt_token(
        jwk_private_key_one,
        {
            "iss": f"https://sts.windows.net/{settings.ENTRA_TENANT_ID}/",
            "sub": "username",
            "appid": settings.ENTRA_APP_ID,
            "roles": ["application.read"],
        },
    )
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    with pytest.raises(validator.TokenError):
        auth.validate(token)


@pytest.mark.parametrize(
    "is_cache_enabled,responses_calls", [(None, 2), (False, 2), (True, 1)]
)
def test_validate_token_caching_entra(
    entra_well_known_keys,
    jwk_private_key_one,
    settings,
    responses,
    is_cache_enabled,
    responses_calls,
):
    if is_cache_enabled is not None:
        settings.ENTRA_PUBLIC_KEYS_CACHING_ENABLED = is_cache_enabled

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
    auth = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    auth.validate(token)
    assert len(responses.calls) == 1

    auth_again = validator.EntraTokenValidator(
        settings.ENTRA_TENANT_ID, settings.ENTRA_AUDIENCE, settings.ENTRA_APP_ID
    )
    auth_again.validate(token)
    assert len(responses.calls) == responses_calls
