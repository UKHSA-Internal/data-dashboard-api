from typing import Optional
from urllib.parse import urljoin

import requests
from rest_framework.response import Response

from caching.internal_api_client import InternalAPIClient


class FrontEndCrawler:
    """This is used to traverse the front end and send GET requests to all relevant pages

    Notes:
        Under the hood, this uses the `InternalAPIClient` to get a list of all pages from the CMS.
        From this point, a simple GET request is made to each page.
        The CDN auth key for the rule on the front end should also be provided.
        If not 403 Forbidden errors will be returned and the cache will not be hydrated.

    """

    def __init__(
        self,
        frontend_base_url: str,
        cdn_auth_key: str,
        internal_api_client: Optional[InternalAPIClient] = None,
    ):
        self._frontend_base_url = frontend_base_url
        self._cdn_auth_key = cdn_auth_key
        self._internal_api_client = internal_api_client or InternalAPIClient()

    @classmethod
    def create_crawler_for_cache_refresh(
        cls, frontend_base_url: str, cdn_auth_key: str
    ) -> "FrontEndCrawler":
        return cls(frontend_base_url=frontend_base_url, cdn_auth_key=cdn_auth_key)

    # Private API/headless CMS API

    def get_all_page_items_from_api(self) -> list[dict]:
        """Hits the `pages/` endpoint to list all page items in the CMS

        Returns:
            List of page items information

        """
        response: Response = self._internal_api_client.hit_pages_list_endpoint()
        return response.json()["items"]

    # Frontend requests

    def hit_frontend_page(self, url: str) -> Response:
        """Hits the frontend page for the given `url`

        Notes:
            This should be used in conjunction with
            the `_build_url_for` methods

        Args:
            url: The full URL of the page to hit

        Returns:
            None

        """
        cdn_auth_key = f'"{self._cdn_auth_key}"'
        requests.get(url=url, headers={"x-cdn-auth": cdn_auth_key})

    def process_page(self, page_item: dict) -> None:
        """Hit the URL for the corresponding `page_item`

        Notes:
            Only the following page types are supported:
            - "HomePage"
            - "TopicPage"
            - "CommonPage"

        Args:
            page_item: The individual page information
                taken from the `pages/` list response

        Returns:
            None

        """
        page_type: str = page_item["type"]

        match page_type:
            case "home.HomePage":
                url = self._build_url_for_home_page()
            case "topic.TopicPage":
                url = self._build_url_for_topic_page(slug=page_item["slug"])
            case "common.CommonPage":
                url = self._build_url_for_common_page(slug=page_item["slug"])
            case _:
                # Pass over for root page objects
                return

        self.hit_frontend_page(url=url)

    def process_all_pages(self) -> None:
        """Traverse the frontend and make a GET request to all relevant pages

        Returns:
            None

        """

        all_page_items: list[dict] = self.get_all_page_items_from_api()

        for page_item in all_page_items:
            self.process_page(page_item=page_item["meta"])

        self.hit_frontend_page(url=self._build_url_for_feedback_confirmation_page())

    # URL construction

    def _build_url_for_topic_page(self, slug: str) -> str:
        """Builds the full URL for the given topic page `slug`

        Args:
            slug: The slug associated with the Topic page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._frontend_base_url, f"/topics/{slug}")

    def _build_url_for_common_page(self, slug: str) -> str:
        """Builds the full URL for the given common page `slug`

        Args:
            slug: The slug associated with the Common page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._frontend_base_url, f"/{slug}")

    def _build_url_for_home_page(self) -> str:
        """Builds the full URL for the single home page

        Returns:
            The full URL which can be passed to requests

        """
        return self._frontend_base_url

    def _build_url_for_feedback_confirmation_page(self) -> str:
        """Builds the full URL for the feedback confirmation page

        Returns:
            The full URL which can be passed to requests

        """
        return urljoin(self._frontend_base_url, "/feedback/confirmation")
