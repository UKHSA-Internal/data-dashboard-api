import logging
from enum import Enum

import requests
from rest_framework.response import Response

from caching.common.geographies_crawler import (
    GeographiesAPICrawler,
    GeographyData,
)
from caching.common.pages import get_pages_for_area_selector
from caching.frontend.threading import call_with_star_map_multithreading
from caching.frontend.urls import FrontEndURLBuilder
from caching.internal_api_client import InternalAPIClient
from cms.topic.models import TopicPage

DEFAULT_REQUEST_TIMEOUT = 60

logger = logging.getLogger(__name__)


class CMSPageTypes(Enum):
    home_page = "home.HomePage"
    topic_page = "topic.TopicPage"
    common_page = "common.CommonPage"
    whats_new_parent_page = "whats_new.WhatsNewParentPage"
    whats_new_child_entry = "whats_new.WhatsNewChildEntry"
    metrics_documentation_parent_page = (
        "metrics_documentation.MetricsDocumentationParentPage"
    )
    metrics_documentation_child_entry = (
        "metrics_documentation.MetricsDocumentationChildEntry"
    )


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
        internal_api_client: InternalAPIClient | None = None,
        frontend_url_builder: FrontEndURLBuilder | None = None,
        geographies_api_crawler: GeographiesAPICrawler | None = None,
    ):
        self._frontend_base_url = frontend_base_url
        self._cdn_auth_key = cdn_auth_key
        self._internal_api_client = internal_api_client or InternalAPIClient()
        self._url_builder = frontend_url_builder or FrontEndURLBuilder(
            base_url=self._frontend_base_url
        )
        self._geographies_api_crawler = (
            geographies_api_crawler
            or GeographiesAPICrawler(internal_api_client=self._internal_api_client)
        )

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

    def hit_frontend_page(
        self, url: str, params: dict[str, str] | None = None
    ) -> Response:
        """Hits the frontend page for the given `url`

        Notes:
            This should be used in conjunction with
            the `_build_url_for` methods

        Args:
            url: The full URL of the page to hit
            params: Optional dict of query parameters

        Returns:
            None

        """
        cdn_auth_key = f'"{self._cdn_auth_key}"'
        requests.get(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers={"x-cdn-auth": cdn_auth_key},
            params=params,
        )
        logger.info("Processed `%s`", url)

    def process_page(self, page_item: dict) -> None:
        """Hit the URL for the corresponding `page_item`

        Notes:
            Only the following page types are supported:
            - "HomePage"
            - "TopicPage"
            - "CommonPage"
            - "WhatsNewParentPage"
            - "WhatsNewChildEntry"
            - "MetricsDocumentationParentPage"
            - "MetricsDocumentationChildEntry"

        Args:
            page_item: The individual page information
                taken from the `pages/` list response

        Returns:
            None

        """
        page_type: str = page_item["type"]

        match page_type:
            case CMSPageTypes.home_page.value:
                url = self._url_builder.build_url_for_home_page()
            case CMSPageTypes.topic_page.value:
                url = self._url_builder.build_url_for_topic_page(slug=page_item["slug"])
            case CMSPageTypes.common_page.value:
                url = self._url_builder.build_url_for_common_page(
                    slug=page_item["slug"]
                )
            case CMSPageTypes.whats_new_parent_page.value:
                url = self._url_builder.build_url_for_whats_new_parent_page()
            case CMSPageTypes.whats_new_child_entry.value:
                url = self._url_builder.build_url_for_whats_new_child_entry(
                    slug=page_item["slug"]
                )
            case CMSPageTypes.metrics_documentation_parent_page.value:
                url = (
                    self._url_builder.build_url_for_metrics_documentation_parent_page()
                )
            case CMSPageTypes.metrics_documentation_child_entry.value:
                url = self._url_builder.build_url_for_metrics_documentation_child_entry(
                    slug=page_item["slug"]
                )
            case _:
                # Pass over for root page objects
                return

        self.hit_frontend_page(url=url)

    def process_all_pages(self) -> None:
        """Traverse the frontend and make a GET request to all relevant pages

        Returns:
            None

        """
        logger.info("Getting all pages from Headless CMS API")
        all_page_items: list[dict] = self.get_all_page_items_from_api()

        for page_item in all_page_items:
            self.process_page(page_item=page_item["meta"])

        self.hit_frontend_page(
            url=self._url_builder.build_url_for_feedback_confirmation_page()
        )
        logger.info("Finished processing all regular pages for the frontend")

    def process_geography_page_combination(
        self, geography_data: GeographyData, page: TopicPage
    ) -> None:
        """Hits the frontend URL for the given `geography_data` and `page` combination

        Args:
            geography_data: An enriched model containing the
                `geography_type_name` and `name` of the geography
            page: The area selector-enabled page to be crawled
                for the given `geography_data`

        Returns:
            None

        """
        url: str = self._url_builder.build_url_for_topic_page(slug=page.slug)
        params: dict[str, str] = (
            self._url_builder.build_query_params_for_area_selector_page(
                geography_type_name=geography_data.geography_type_name,
                geography_name=geography_data.name,
            )
        )
        logger.info(
            "Hitting area selector URL for `%s` for %s:%s",
            url,
            geography_data.geography_type_name,
            geography_data.name,
        )
        self.hit_frontend_page(url=url, params=params)

    def process_geography_page_combinations(self, page: TopicPage) -> None:
        """Crawls the given `page` for all the relevant geography combinations

        Notes:
            This method will crawl the geography combinations
            for the page with a pool of threads

        Args:
            page: The area selector-enabled page
                to be processed

        Returns:
            None

        """
        geography_combinations: list[GeographyData] = (
            self._geographies_api_crawler.get_geography_combinations_for_page(page=page)
        )

        args = [(geography_data, page) for geography_data in geography_combinations]
        call_with_star_map_multithreading(
            func=self.process_geography_page_combination,
            items=args,
            thread_count=100,
        )

    def process_all_valid_area_selector_pages(self) -> None:
        """Crawls all valid area selector-enables pages for corresponding geography combinations

        Notes:
            This method will crawl the geography combinations
            for each of the valid pages with a pool of threads

        Returns:
            None

        """
        logger.info("Crawling for area selector URLs")

        area_selector_pages: list[TopicPage] = get_pages_for_area_selector()
        for area_selector_page in area_selector_pages:
            self.process_geography_page_combinations(page=area_selector_page)
