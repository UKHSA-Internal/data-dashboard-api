import logging
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)

DEFAULT_REQUEST_TIMEOUT = 60


class PublicAPICrawler:
    """This is used to traverse the public API and send GET requests to all relevant routes

    Notes:
        The CDN auth key for the rule on the public API should also be provided.
        If not 403 Forbidden errors will be returned and the API will not be crawled.

    """

    def __init__(
        self,
        *,
        public_api_base_url: str,
        cdn_auth_key: str,
        request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
    ):
        self._public_api_base_url = public_api_base_url
        self._cdn_auth_key = cdn_auth_key
        self._request_timeout = request_timeout

    @classmethod
    def create_crawler_for_cache_refresh(
        cls, *, public_api_base_url: str, cdn_auth_key: str
    ) -> "PublicAPICrawler":
        return cls(public_api_base_url=public_api_base_url, cdn_auth_key=cdn_auth_key)

    # Headers construction

    def _build_base_headers(self) -> dict[str, str]:
        """Constructs base headers which should be used in all requests

        Notes:
            In this case, the CDN auth key is constructed

        Returns:
            Dict containing base header key-value pairs

        """
        return {"x-cdn-auth": self._cdn_auth_key}

    def build_headers_for_html(self) -> dict[str, str]:
        """Constructs headers which should be used in HTML requests

        Notes:
            In this case, the CDN auth key is constructed.
            And the "Accept" header is provided as "text/html"

        Returns:
            Dict containing the necessary header key-value pairs

        """
        headers = self._build_base_headers()
        headers["Accept"] = "text/html"
        return headers

    def build_headers_for_json(self) -> dict[str, str]:
        """Constructs headers which should be used in JSON requests

        Notes:
            In this case, the CDN auth key is constructed.
            And the "Accept" header is provided as "application/json"

        Returns:
            Dict containing the necessary header key-value pairs

        """
        headers = self._build_base_headers()
        headers["Accept"] = "application/json"
        return headers

    # Endpoint call methods

    def _hit_endpoint_with_base_headers(self, *, url: str) -> dict:
        """Makes a `GET` request to the given `url` for a JSON response

        Args:
            url: The URL to make the request to

        Returns:
            Dict containing the JSON response data

        """
        response = requests.get(
            url=url,
            timeout=self._request_timeout,
            headers=self._build_base_headers(),
        )
        return response.json()

    def _hit_endpoint_with_accept_json(self, *, url: str) -> str:
        """Makes a 'GET' request to the given 'url' for a JSON response

        Args:
            url: The URL to amke the request to

        Returns:
            JSON content containing the response

        """
        headers = self.build_headers_for_json()
        response = requests.get(
            url=url,
            timeout=self._request_timeout,
            headers=headers,
        )

        return response.content

    def _hit_endpoint_with_accept_html(self, *, url: str) -> str:
        """Makes a `GET` request to the given `url` for an HTML response

        Args:
            url: The URL to make the request to

        Returns:
            A string containing the HTML response content

        """
        headers = self.build_headers_for_html()
        response = requests.get(
            url=url,
            timeout=self._request_timeout,
            headers=headers,
        )

        return response.content

    def hit_endpoint(self, *, url: str) -> dict:
        """Hit the given `url` for the different response types (JSON & HTML).

        Args:
            url: The URL to make the request to

        Returns:
            Dict containing the JSON response data

        """
        self._hit_endpoint_with_accept_html(url=url)
        self._hit_endpoint_with_accept_json(url=url)
        return self._hit_endpoint_with_base_headers(url=url)

    @staticmethod
    def _is_url(*, value: str) -> bool:
        """Determines whether the given `value` is a URL

        Args:
            value: The string being checked

        Returns:
            True if `value` is a URL, False otherwise.

        """
        return "http" in value

    # Recursive crawl

    def crawl(self, *, url: str, crawled_urls: list[str]) -> list[str]:
        """Traverses the hyperlinked API by recursively crawling the given `url`

        Args:
            url: The URL to traverse
            crawled_urls: List of URLs which have been crawled

        Returns:
            List of URLs which have been crawled.
            This is subsequently passed to another call to this method.

        """
        logger.info("Calling %s", url)
        response_data: dict = self.hit_endpoint(url=url)

        targets: list[str] = self.get_links_from_response_data(
            response_data=response_data
        )

        for target in targets:
            if target not in crawled_urls:
                crawled_urls.append(target)
                try:
                    self.crawl(url=target, crawled_urls=crawled_urls)
                except requests.exceptions.RequestException as error:
                    logger.info("`%s` could not be crawled due to: %s", target, error)
                else:
                    logger.info("%s URLs crawled", len(crawled_urls))

        return crawled_urls

    def get_links_from_response_data(self, *, response_data: dict) -> list[str]:
        """Extracts all link from the given `response_data`

        Args:
            response_data: Dict of response data from
                the previous endpoint call

        Returns:
            List of string representing the links
            contained within the `response_data`

        """
        targets = []
        for links in response_data:
            if isinstance(links, dict):
                for value in links.values():
                    if self._is_url(value=value):
                        targets.append(value)

        return targets

    # Processing API

    def crawl_public_api_themes_path(self) -> None:
        """Crawls the public API from the root `themes/` path

        Returns:
            None

        """
        public_api_themes_root_path = self._build_themes_root_path()
        logger.info("Crawling from root URL %s", public_api_themes_root_path)
        self.crawl(url=public_api_themes_root_path, crawled_urls=[])

    def _build_themes_root_path(self) -> str:
        """Builds the full URL for the root themes/ path

        Returns:
            The full URL for the root themes path
            which can be passed to requests

        """
        return urljoin(base=self._public_api_base_url, url="themes/")

    def process_all_routes(self) -> None:
        """Crawls the public API in its entirety

        Notes:
            Currently only the `themes/` path is supported.
            This will also only traverse the mandatory URL parameters.
            The section of the API controlled by query parameters will not be crawled.

        Returns:
            None

        """
        self.crawl_public_api_themes_path()
