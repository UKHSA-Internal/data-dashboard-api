from rest_framework.authentication import TokenAuthentication
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import BaseHasAPIKey

KEYWORD: str = "Authorization"


class HasApiKeyHeader(BaseHasAPIKey):
    keyword = KEYWORD
    model = APIKey


class TokenHeaderAuthentication(TokenAuthentication):
    keyword = KEYWORD
