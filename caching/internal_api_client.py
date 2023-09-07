from typing import Optional

from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey

from metrics.data.managers.api_keys import CustomAPIKeyManager

API_PREFIX = "/api/"
HEADLINES_ENDPOINT_PATH = f"{API_PREFIX}headlines/v2/"
TRENDS_ENDPOINT_PATH = f"{API_PREFIX}trends/v2/"
CHARTS_ENDPOINT_PATH = f"{API_PREFIX}charts/v3/"
TABLES_ENDPOINT_PATH = f"{API_PREFIX}tables/v2/"


class InternalAPIClient:
    """The client used to interact with the private API

    Notes:
        This client is used to crawl the site and hit the various endpoints.
        In turn, the requests made to the endpoint will persist within the cache.
        This should be used to emulate inbound requests.

    """

    def __init__(
        self,
        client: Optional[APIClient] = None,
        api_key_manager: Optional[CustomAPIKeyManager] = None,
    ):
        self._api_key_manager = api_key_manager or self.create_api_key_manager()
        self._client = client or self.create_api_client()

        self.headlines_endpoint_path = HEADLINES_ENDPOINT_PATH
        self.trends_endpoint_path = TRENDS_ENDPOINT_PATH
        self.charts_endpoint_path = CHARTS_ENDPOINT_PATH
        self.tables_endpoint_path = TABLES_ENDPOINT_PATH

    @property
    def temporary_api_key_name(self) -> str:
        return "Crawler Key"

    def create_api_client(self) -> APIClient:
        """Initializes a new `APIClient` which can be used to emulate requests made to the private API.

        Returns:
            An authenticated `APIClient` instance

        """
        _, key = self._api_key_manager.create_key(name=self.temporary_api_key_name)

        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION=key)

        return api_client

    @staticmethod
    def create_api_key_manager() -> CustomAPIKeyManager:
        """Initializes a new `CustomAPIKeyManager` which can be used to create a valid API key

        Returns:
            A `CustomAPIKeyManager` instance with the `APIKey` model set
        """
        api_key_manager = CustomAPIKeyManager()
        api_key_manager.model = APIKey
        return api_key_manager

    def hit_headlines_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `GET` request to the `headlines/` endpoint with the given `data`

        Args:
            data: A dict representing the query parameters

        Returns:
            `Response` from the `headlines/` endpoint

        """
        path = self.headlines_endpoint_path
        return self._client.get(path=path, data=data)

    def hit_trends_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `GET` request to the `trends/` endpoint with the given `data`

        Args:
            data: A dict representing the query parameters

        Returns:
            `Response` from the `trends/` endpoint

        """
        path = self.trends_endpoint_path
        return self._client.get(path=path, data=data)

    def hit_charts_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `charts/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `charts/` endpoint

        """
        path = self.charts_endpoint_path
        return self._client.post(path=path, data=data, format="json")

    def hit_tables_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `tables/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `tables/` endpoint

        """
        path = self.tables_endpoint_path
        return self._client.post(path=path, data=data, format="json")
