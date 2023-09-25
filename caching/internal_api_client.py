from typing import Optional

from rest_framework.response import Response
from rest_framework.test import APIClient

API_PREFIX = "/api/"
PAGES_ENDPOINT_PATH = f"{API_PREFIX}pages/"
HEADLINES_ENDPOINT_PATH = f"{API_PREFIX}headlines/v2/"
TRENDS_ENDPOINT_PATH = f"{API_PREFIX}trends/v2/"
CHARTS_ENDPOINT_PATH = f"{API_PREFIX}charts/v3/"
TABLES_ENDPOINT_PATH = f"{API_PREFIX}tables/v3/"
DOWNLOADS_ENDPOINT_PATH = f"{API_PREFIX}downloads/v2/"


CACHE_FORCE_REFRESH_HEADER_KEY = "Cache-Force-Refresh"
CACHE_CHECK_HEADER_KEY = "Cache-Check"


PAGE_TYPES = ("common.CommonPage", "topic.TopicPage", "home.HomePage")


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
        force_refresh: bool = False,
        cache_check_only: bool = False,
    ):
        self._client = client or self.create_api_client()

        # Endpoints
        self.pages_endpoint_path = PAGES_ENDPOINT_PATH
        self.headlines_endpoint_path = HEADLINES_ENDPOINT_PATH
        self.trends_endpoint_path = TRENDS_ENDPOINT_PATH
        self.charts_endpoint_path = CHARTS_ENDPOINT_PATH
        self.tables_endpoint_path = TABLES_ENDPOINT_PATH
        self.downloads_endpoint_path = DOWNLOADS_ENDPOINT_PATH

        # Header configurations
        self.force_refresh = force_refresh
        self.cache_check_only = cache_check_only

    # API client

    @staticmethod
    def create_api_client() -> APIClient:
        """Initializes a new `APIClient` which can be used to emulate requests made to the private API.

        Returns:
            An `APIClient` instance

        """
        return APIClient()

    # Headers

    def build_headers(self) -> dict[str, bool]:
        return {
            CACHE_FORCE_REFRESH_HEADER_KEY: self.force_refresh,
            CACHE_CHECK_HEADER_KEY: self.cache_check_only,
        }

    # Endpoints

    def hit_headlines_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `GET` request to the `headlines/` endpoint with the given `data`

        Args:
            data: A dict representing the query parameters

        Returns:
            `Response` from the `headlines/` endpoint

        """
        path = self.headlines_endpoint_path
        headers = self.build_headers()
        return self._client.get(path=path, data=data, headers=headers)

    def hit_trends_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `GET` request to the `trends/` endpoint with the given `data`

        Args:
            data: A dict representing the query parameters

        Returns:
            `Response` from the `trends/` endpoint

        """
        path = self.trends_endpoint_path
        headers = self.build_headers()
        return self._client.get(path=path, data=data, headers=headers)

    def hit_charts_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `charts/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `charts/` endpoint

        """
        path = self.charts_endpoint_path
        headers = self.build_headers()
        return self._client.post(path=path, data=data, headers=headers, format="json")

    def hit_tables_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `tables/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `tables/` endpoint

        """
        path = self.tables_endpoint_path
        headers = self.build_headers()
        return self._client.post(path=path, data=data, headers=headers, format="json")

    def hit_downloads_endpoint(self, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `downloads/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `downloads/` endpoint

        """
        path = self.downloads_endpoint_path
        headers = self.build_headers()
        return self._client.post(path=path, data=data, headers=headers, format="json")

    def hit_pages_list_endpoint(self) -> Response:
        """Sends a `GET` request to the list `pages/` endpoint.

        Returns:
            `Response` from the list `pages/` endpoint

        """
        path = self.pages_endpoint_path
        headers = self.build_headers()
        return self._client.get(path=path, headers=headers, format="json")

    def hit_pages_list_endpoint_for_page_type_query_param(
        self, page_type_query_param: str
    ) -> Response:
        """Sends a `GET` request to the list `pages/` endpoint with a query param for the given page type

        Args:
            page_type_query_param: The query parameter for the page type
                E.g. "topic.TopicPage"

        Returns:
            `Response` from the list `pages/?type=` endpoint

        """
        path = self.pages_endpoint_path
        headers = self.build_headers()
        return self._client.get(
            path=path,
            headers=headers,
            data={"type": page_type_query_param},
            format="json",
        )

    def hit_pages_list_endpoint_for_all_page_types(self) -> None:
        """Sends a `GET` request to the list `pages/` endpoint with a query param for each page type

        Returns:
            None

        """
        for page_type in PAGE_TYPES:
            self.hit_pages_list_endpoint_for_page_type_query_param(
                page_type_query_param=page_type
            )

    def hit_pages_detail_endpoint(self, page_id: int) -> Response:
        """Sends a `GET` request to the detail `pages/` endpoint for the given `page_id`

        Returns:
            `Response` from the detail `pages/` endpoint

        """
        path = f"{self.pages_endpoint_path}{page_id}"
        headers = self.build_headers()
        self._client.get(path=f"{path}/", headers=headers, format="json")
        return self._client.get(path=path, headers=headers, format="json")
