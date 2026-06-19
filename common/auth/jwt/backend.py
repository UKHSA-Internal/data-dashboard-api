import logging

import jwt
from django.apps import apps as django_apps
from django.conf import settings
from django.utils.encoding import force_str
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import BaseAuthentication

from .validator import CognitoTokenValidator, EntraTokenValidator, TokenError

logger = logging.getLogger(__name__)

# 2 objects expected when parsing Auth Header: 'Bearer' + token
VALID_AUTH_HEADER_LENGTH = 2


def get_authorization_header(request):
    """
    Return request's authentication header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth_header = getattr(settings, "JWT_AUTH_HEADER", "HTTP_AUTHORIZATION")
    auth = request.META.get(auth_header, b"")

    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class JSONWebTokenAuthentication(BaseAuthentication):
    """Token based authentication using the JSON Web Token standard.
    Based on https://github.com/labd/django-cognito-jwt and modified
    to suit our use case
    """

    def authenticate(self, request):
        """Entrypoint for Django Rest Framework"""
        jwt_token = self.get_jwt_token(request)
        if jwt_token is None:
            return None

        # Authenticate token
        try:
            token_validator, provider_name = self.get_token_validator(jwt_token)
        except TokenError as e:
            logger.debug("Failed to identify token provider: %s", e)
            raise exceptions.AuthenticationFailed(
                _("Unknown or malformed token issuer.")
            ) from e

        try:
            jwt_payload = token_validator.validate(jwt_token)
        except TokenError as e:
            logger.debug(
                "%s token validation failed: %s", provider_name.capitalize(), e
            )
            raise exceptions.AuthenticationFailed from None

        custom_user_manager = self.get_custom_user_manager(provider_name)

        if custom_user_manager:
            user = custom_user_manager.get_or_create(jwt_payload)
        else:
            user_model = self.get_user_model()
            user = user_model.objects.get_or_create(jwt_payload)
        if not user:
            logger.debug(
                "Unable to create user from JWT, defaulting to unauthenticated"
            )
            return None

        return (user, jwt_token)

    @staticmethod
    def get_custom_user_manager(provider="cognito"):
        """If COGNITO_USER_MANAGER or ENTRA_USER_MANAGER is set, then the user object is obtained
        via get_or_create_for_cognito (or get_or_create_for_entra) on the user manager, this allows use
        of the default unmodified Django User model"""
        result = None
        custom_user_manager_path = (
            getattr(settings, "ENTRA_USER_MANAGER", False)
            if provider == "entra"
            else getattr(settings, "COGNITO_USER_MANAGER", False)
        )
        if custom_user_manager_path:
            result = import_string(custom_user_manager_path)()
        return result

    @staticmethod
    def get_user_model(provider="cognito"):
        user_model = (
            getattr(settings, "ENTRA_USER_MODEL", settings.AUTH_USER_MODEL)
            if provider == "entra"
            else getattr(settings, "COGNITO_USER_MODEL", settings.AUTH_USER_MODEL)
        )
        return django_apps.get_model(user_model, require_ready=False)

    @staticmethod
    def get_jwt_token(request):
        auth = get_authorization_header(request).split()
        if not auth or force_str(auth[0].lower()) != "bearer":
            return None

        if len(auth) == 1:
            msg = _("Invalid Authorization header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) > VALID_AUTH_HEADER_LENGTH:
            msg = _(
                "Invalid Authorization header. Credentials string "
                "should not contain spaces."
            )
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    @staticmethod
    def get_token_validator(jwt_token):
        try:
            # Decode without verifying signature just to read the header/payload
            unverified_payload = jwt.decode(
                jwt_token, options={"verify_signature": False}  # noqa: S5659
            )
            issuer = unverified_payload.get("iss", "")
        except jwt.PyJWTError as e:
            raise exceptions.AuthenticationFailed(_("Malformed JWT.")) from e

        if "cognito-idp" in issuer:
            validator = CognitoTokenValidator(
                settings.COGNITO_AWS_REGION,
                settings.COGNITO_USER_POOL,
                settings.COGNITO_AUDIENCE,
            )
            return validator, "cognito"

        if "sts.windows.net" in issuer:
            validator = EntraTokenValidator(
                settings.ENTRA_TENANT_ID,
                settings.ENTRA_AUDIENCE,
                settings.ENTRA_APP_ID,
            )
            return validator, "entra"

        raise exceptions.AuthenticationFailed(_("Invalid or unsupported token issuer."))

    @staticmethod
    def authenticate_header(request):
        """
        Method required by the DRF in order to return 401 responses for authentication failures, instead of 403.
        More details in https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication.
        """
        return "Bearer: api"
