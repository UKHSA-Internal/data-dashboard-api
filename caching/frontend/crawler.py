import logging
from collections.abc import Iterator

import requests
from defusedxml import ElementTree
from rest_framework.response import Response

from caching.common.geographies_crawler import (
    GeographiesAPICrawler,
    GeographyData,
)
from caching.common.pages import get_pages_for_area_selector
from caching.frontend.multi_threading import call_with_star_map_multithreading
from caching.frontend.urls import FrontEndURLBuilder
from caching.internal_api_client import InternalAPIClient
from cms.topic.models import TopicPage

DEFAULT_REQUEST_TIMEOUT = 60
PAGE_XML_LOCATOR = ".//ns:loc"

logger = logging.getLogger(__name__)


class FrontEndCrawler:
    """This is used to traverse the front end and send GET requests to all relevant pages

    Notes:
        Under the hood, this gathers all the URLs in the front end from the associated sitemap.xml
        From this point, a simple GET request is made to each page.
        The CDN auth key for the rule on the front end should also be provided.
        If not 403 Forbidden errors will be returned and the cache will not be hydrated.

    """

    def __init__(
        self,
        *,
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

    @property
    def sitemap_url(self) -> str:
        return self._url_builder.build_url_for_sitemap()

    def _hit_sitemap_url(self) -> Response:
        url: str = self.sitemap_url
        return requests.get(url=url, timeout=DEFAULT_REQUEST_TIMEOUT)

    def _parse_sitemap(self):
        response: Response = self._hit_sitemap_url()
        xml_response_data: str = response.content.decode("utf-8")
        return ElementTree.fromstring(text=xml_response_data)

    def _traverse_sitemap(self) -> Iterator[str]:
        sitemap_root = self._parse_sitemap()
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return (
            loc.text
            for loc in sitemap_root.findall(PAGE_XML_LOCATOR, namespaces=namespace)
        )

    def process_all_page_urls(self) -> None:
        """Traverse the frontend and make a GET request to all relevant pages

        Returns:
            None

        """
        logger.info("Traversing sitemap for URLs")

        urls: Iterator[str] = self._traverse_sitemap()

        for url in urls:
            logger.info("Processing `%s`", url)
            self.hit_frontend_page(url=url)

        logger.info("Finished processing all URLs for the frontend")

    @classmethod
    def create_crawler_for_cache_refresh(
        cls, *, frontend_base_url: str, cdn_auth_key: str
    ) -> "FrontEndCrawler":
        return cls(frontend_base_url=frontend_base_url, cdn_auth_key=cdn_auth_key)

    # Frontend requests

    def hit_frontend_page(
        self, *, url: str, params: dict[str, str] | None = None
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
        logger.info("Processed `%s` for params: %s", url, params)

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
        url: str = page.full_url
        params: dict[str, str] = (
            self._url_builder.build_query_params_for_area_selector_page(
                geography_type_name=geography_data.geography_type_name,
                geography_name=geography_data.name,
            )
        )
        try:
            self.hit_frontend_page(url=url, params=params)
        except Exception:  # noqa: BLE001
            # Broad exception to fail silently
            # because we run this method in a pool of threads
            # we expect to see flakiness in requests being made over network.
            # If we cannot crawl the odd page/geography combo here and there
            # it is not the end of the world as that
            # request from the user will just go to redis
            logger.warning("`%s` with params of `%s` could not be hit", url, params)

    def process_geography_page_combinations(self, *, page: TopicPage) -> None:
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
