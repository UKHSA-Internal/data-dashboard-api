from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if (
        response is not None
        and response.status_code == status.HTTP_403_FORBIDDEN
        and isinstance(exc, AuthenticationFailed)
    ):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response["WWW-Authenticate"] = 'Bearer realm="api"'

    return response
