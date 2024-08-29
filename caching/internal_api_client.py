from urllib.parse import urljoin

from rest_framework.response import Response
from rest_framework.test import APIClient

API_PREFIX = "/api/"
PAGES_ENDPOINT_PATH = f"{API_PREFIX}pages/"
HEADLINES_ENDPOINT_PATH = f"{API_PREFIX}headlines/v3/"
TRENDS_ENDPOINT_PATH = f"{API_PREFIX}trends/v3/"
CHARTS_ENDPOINT_PATH = f"{API_PREFIX}charts/v3/"
TABLES_ENDPOINT_PATH = f"{API_PREFIX}tables/v4/"
DOWNLOADS_ENDPOINT_PATH = f"{API_PREFIX}downloads/v2/"
GEOGRAPHIES_ENDPOINT_PATH = f"{API_PREFIX}geographies/v2/"
GLOBAL_BANNERS_ENDPOINT_PATH = f"{API_PREFIX}global-banners/v1"
MENUS_ENDPOINT_PATH = f"{API_PREFIX}menus/v1"


CACHE_FORCE_REFRESH_HEADER_KEY = "Cache-Force-Refresh"
CACHE_CHECK_HEADER_KEY = "Cache-Check"


PAGE_TYPES_WITH_NO_ADDITIONAL_QUERY_PARAMS = (
    "common.CommonPage",
    "topic.TopicPage",
    "home.HomePage",
)


class InternalAPIClient:
    """The client used to interact with the private API

    Notes:
        This client is used to crawl the site and hit the various endpoints.
        In turn, the requests made to the endpoint will persist within the cache.
        This should be used to emulate inbound requests.

    """

    def __init__(
        self,
        *,
        client: APIClient | None = None,
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
        self.geographies_endpoint_path = GEOGRAPHIES_ENDPOINT_PATH
        self.global_banners_endpoint_path = GLOBAL_BANNERS_ENDPOINT_PATH
        self.menus_endpoint_path = MENUS_ENDPOINT_PATH

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

    # Query parameters

    @staticmethod
    def build_query_params(
        *, page_type: str, additional_query_params: dict[str, str] | None = None
    ) -> dict[str, str]:
        additional_query_params = additional_query_params or {}
        return {"type": page_type, **additional_query_params}

    # Endpoints

    def hit_headlines_endpoint(self, *, data: dict[str, str]) -> Response:
        """Sends a `GET` request to the `headlines/` endpoint with the given `data`

        Args:
            data: A dict representing the query parameters

        Returns:
            `Response` from the `headlines/` endpoint

        """
        path = self.headlines_endpoint_path
        headers = self.build_headers()
        return self._client.get(path=path, data=data, headers=headers)

    def hit_trends_endpoint(self, *, data: dict[str, str]) -> Response:
        """Sends a `GET` request to the `trends/` endpoint with the given `data`

        Args:
            data: A dict representing the query parameters

        Returns:
            `Response` from the `trends/` endpoint

        """
        path = self.trends_endpoint_path
        headers = self.build_headers()
        return self._client.get(path=path, data=data, headers=headers)

    def hit_charts_endpoint(self, *, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `charts/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `charts/` endpoint

        """
        path = self.charts_endpoint_path
        headers = self.build_headers()
        return self._client.post(path=path, data=data, headers=headers, format="json")

    def hit_tables_endpoint(self, *, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `tables/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `tables/` endpoint

        """
        headers = self.build_headers()
        return self._client.post(
            path=self.tables_endpoint_path, data=data, headers=headers, format="json"
        )

    def hit_downloads_endpoint(self, *, data: dict[str, str]) -> Response:
        """Sends a `POST` request to the `downloads/` endpoint with the given `data`

        Args:
            data: A dict representing the request body

        Returns:
            `Response` from the `downloads/` endpoint

        """
        path = self.downloads_endpoint_path
        headers = self.build_headers()
        return self._client.post(path=path, data=data, headers=headers, format="json")

    def hit_geographies_list_endpoint(self, *, topic: str) -> Response:
        """Sends a `GET` request to the list `geographies/` endpoint

        Returns:
            `Response` from the `geographies/` endpoint

        """
        path: str = urljoin(base=self.geographies_endpoint_path, url=topic)
        headers: dict[str, bool] = self.build_headers()
        return self._client.get(path=path, headers=headers, format="json")

    def hit_pages_list_endpoint(self) -> Response:
        """Sends a `GET` request to the list `pages/` endpoint.

        Returns:
            `Response` from the list `pages/` endpoint

        """
        path = self.pages_endpoint_path
        headers = self.build_headers()
        return self._client.get(path=path, headers=headers, format="json")

    def hit_pages_list_endpoint_for_page_type(
        self,
        *,
        page_type_query_param: str,
        additional_query_params: dict[str, str] | None = None,
    ) -> Response:
        """Sends a `GET` request to the list `pages/` endpoint with a query param for the given page type

        Args:
            page_type_query_param: The query parameter for the page type
                E.g. "topic.TopicPage"
            additional_query_params: Dict of additional query parameters
                to be passed to the request

        Returns:
            `Response` from the list `pages/?type=` endpoint

        """
        path: str = self.pages_endpoint_path
        headers: dict[str, str] = self.build_headers()

        query_params: dict[str, str] = self.build_query_params(
            page_type=page_type_query_param,
            additional_query_params=additional_query_params,
        )

        return self._client.get(
            path=path,
            headers=headers,
            data=query_params,
            format="json",
        )

    def hit_pages_list_endpoint_for_all_page_types(self) -> None:
        """Sends a `GET` request to the list `pages/` endpoint with a query param for each page type

        Returns:
            None

        """
        for page_type in PAGE_TYPES_WITH_NO_ADDITIONAL_QUERY_PARAMS:
            self.hit_pages_list_endpoint_for_page_type(page_type_query_param=page_type)

        # The whats_new page types have bespoke query parameters which need to be cached
        self.hit_pages_list_endpoint_for_page_type(
            page_type_query_param="whats_new.WhatsNewParentPage",
            additional_query_params={"fields": "date_posted"},
        )
        self.hit_pages_list_endpoint_for_page_type(
            page_type_query_param="whats_new.WhatsNewChildEntry",
            additional_query_params={"fields": "*"},
        )

    def hit_pages_detail_endpoint(self, *, page_id: int) -> Response:
        """Sends a `GET` request to the detail `pages/` endpoint for the given `page_id`

        Returns:
            `Response` from the detail `pages/` endpoint

        """
        path = f"{self.pages_endpoint_path}{page_id}"
        headers = self.build_headers()
        self._client.get(path=f"{path}/", headers=headers, format="json")
        return self._client.get(path=path, headers=headers, format="json")

    def hit_global_banners_endpoint(self) -> Response:
        """Sends a `GET` request to the `global-banners/` endpoint

        Returns:
            `Response` from the `global-banners/` endpoint

        """
        headers = self.build_headers()
        return self._client.get(
            path=self.global_banners_endpoint_path, headers=headers, format="json"
        )

    def hit_menus_endpoint(self) -> Response:
        """Sends a `GET` request to the `menus/` endpoint

        Returns:
            `Response` from the `menus/` endpoint

        """
        headers = self.build_headers()
        return self._client.get(
            path=self.menus_endpoint_path, headers=headers, format="json"
        )
