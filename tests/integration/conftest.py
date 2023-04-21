import pytest
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey


@pytest.fixture
def authenticated_api_client() -> APIClient:
    _, key = APIKey.objects.create_key(name="Test Key")

    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=key)

    return api_client
