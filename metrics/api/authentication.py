from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import BaseHasAPIKey

KEYWORD = "X-Api-Key"
_HEADER_KEY = f"HTTP_{KEYWORD.upper().replace('-', '_')}"

class HasApiKeyHeader(BaseHasAPIKey):
    keyword = KEYWORD
    model = APIKey


class TokenHeaderAuthentication(TokenAuthentication):
    keyword = KEYWORD

    def authenticate(self, request):

        auth = request.headers.get(KEYWORD, "").split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise AuthenticationFailed(msg)

        try:
            # Try to authenticate with the token
            return self.authenticate_credentials(auth[1])
        except AuthenticationFailed as e:
            raise e
