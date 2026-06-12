import json
import logging

import jwt
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.functional import cached_property
from jwt.algorithms import RSAAlgorithm

logger = logging.getLogger(__name__)


class TokenError(Exception):
    pass


class CognitoTokenValidator:
    def __init__(self, aws_region, aws_user_pool, audience):
        self.aws_region = aws_region
        self.aws_user_pool = aws_user_pool
        self.audience = audience

    @cached_property
    def pool_url(self):
        return (
            f"https://cognito-idp.{self.aws_region}.amazonaws.com/{self.aws_user_pool}"
        )

    @cached_property
    def _json_web_keys(self):
        response = requests.get(self.pool_url + "/.well-known/jwks.json", timeout=10)
        response.raise_for_status()
        json_data = response.json()
        return {item["kid"]: json.dumps(item) for item in json_data["keys"]}

    def _get_public_key(self, token):
        try:
            headers = jwt.get_unverified_header(token)
        except jwt.DecodeError as exc:
            raise TokenError(str(exc)) from exc

        if getattr(settings, "COGNITO_PUBLIC_KEYS_CACHING_ENABLED", False):
            cache_key = "cognito_jwt:{}".format(headers["kid"])
            jwk_data = cache.get(cache_key)

            if not jwk_data:
                jwk_data = self._json_web_keys.get(headers["kid"])
                timeout = getattr(settings, "COGNITO_PUBLIC_KEYS_CACHING_TIMEOUT", 300)
                cache.set(cache_key, jwk_data, timeout=timeout)
        else:
            jwk_data = self._json_web_keys.get(headers["kid"])

        if jwk_data:
            return RSAAlgorithm.from_jwk(jwk_data)
        return None

    def validate(self, token):
        public_key = self._get_public_key(token)
        if not public_key:
            msg = "No key found for this token"
            raise TokenError(msg)

        params = {
            "jwt": token,
            "key": public_key,
            "issuer": self.pool_url,
            "algorithms": ["RS256"],
        }

        logger.debug("JWT - %s", params)
        token_payload = jwt.decode(
            token, options={"verify_signature": False}  # noqa: S5659
        )
        logger.debug("JWT decoded - %s", token_payload)

        if "aud" in token_payload:
            params.update({"audience": self.audience})

        try:
            jwt_data = jwt.decode(**params)
        except (
            jwt.InvalidTokenError,
            jwt.ExpiredSignatureError,
            jwt.DecodeError,
        ) as exc:
            raise TokenError(str(exc)) from exc
        return jwt_data


class EntraTokenValidator:
    def __init__(self, tenant_id, audience, app_id):
        self.tenant_id = tenant_id
        self.audience = audience
        self.app_id = app_id

    @cached_property
    def expected_issuer(self):
        return f"https://sts.windows.net/{self.tenant_id}/"

    @cached_property
    def jwks_url(self):
        return "https://login.microsoftonline.com/common/discovery/keys"

    @cached_property
    def _json_web_keys(self):
        response = requests.get(self.jwks_url, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        return {item["kid"]: json.dumps(item) for item in json_data["keys"]}

    def _get_public_key(self, token):
        try:
            headers = jwt.get_unverified_header(token)
        except jwt.DecodeError as exc:
            raise TokenError(str(exc)) from exc

        if getattr(settings, "ENTRA_PUBLIC_KEYS_CACHING_ENABLED", False):
            cache_key = "entra_jwt:{}".format(headers["kid"])
            jwk_data = cache.get(cache_key)

            if not jwk_data:
                jwk_data = self._json_web_keys.get(headers["kid"])
                timeout = getattr(settings, "ENTRA_PUBLIC_KEYS_CACHING_TIMEOUT", 300)
                cache.set(cache_key, jwk_data, timeout=timeout)
        else:
            jwk_data = self._json_web_keys.get(headers["kid"])

        if jwk_data:
            return RSAAlgorithm.from_jwk(jwk_data)
        return None

    def validate(self, token):
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError as exc:
            raise TokenError(str(exc)) from exc

        if "permission_sets" in unverified_payload:
            logger.debug("permission_sets found in token, skipping validation.")
            return unverified_payload

        public_key = self._get_public_key(token)
        if not public_key:
            msg = "No key found for this token"
            raise TokenError(msg)

        params = {
            "jwt": token,
            "key": public_key,
            "issuer": self.expected_issuer,
            "audience": self.audience,
            "algorithms": ["RS256"],
        }

        try:
            payload = jwt.decode(**params)
        except (
            jwt.InvalidTokenError,
            jwt.ExpiredSignatureError,
            jwt.DecodeError,
        ) as exc:
            raise TokenError(str(exc)) from exc

        roles = payload.get("roles", [])
        if "Application.Read" not in roles:
            raise TokenError("Missing required role: Application.Read")

        app_id_claim = payload.get("appid") or payload.get("azp")
        if app_id_claim != self.app_id:
            raise TokenError("Invalid app_id claim")

        return payload
