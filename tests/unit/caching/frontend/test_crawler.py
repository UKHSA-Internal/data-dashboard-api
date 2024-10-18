from typing import Iterator
from unittest import mock
from defusedxml import ElementTree

import pytest
from _pytest.logging import LogCaptureFixture
from requests.exceptions import ChunkedEncodingError

from caching.common.geographies_crawler import GeographyData
from caching.frontend.crawler import DEFAULT_REQUEST_TIMEOUT, FrontEndCrawler

MODULE_PATH = "caching.frontend.crawler"


@pytest.fixture()
def frontend_crawler_with_mocked_internal_api_client() -> FrontEndCrawler:
    return FrontEndCrawler(
        frontend_base_url="https://fake-frontend.co.uk",
        cdn_auth_key="123456789",
        internal_api_client=mock.MagicMock(),
    )


class TestFrontEndCrawler:
    # Frontend requests

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_frontend_page(
        self,
        spy_requests: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a URL
        When `hit_frontend_page()` is called from an instance of `FrontEndCrawler`
        Then a GET request is sent to the URL with the correct headers
        """
        # Given
        url = "https://fake-url.com"

        # When
        frontend_crawler_with_mocked_internal_api_client.hit_frontend_page(url=url)

        # Then
        expected_cdn_auth_key = (
            f'"{frontend_crawler_with_mocked_internal_api_client._cdn_auth_key}"'
        )
        spy_requests.get.assert_called_once_with(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers={"x-cdn-auth": expected_cdn_auth_key},
            params=None,
        )

        assert f"Processed `{url}`" in caplog.text

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_frontend_page_with_query_params(
        self,
        spy_requests: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a URL and a dict for the query parameters
        When `hit_frontend_page()` is called from an instance of `FrontEndCrawler`
        Then a GET request is sent to the URL with the correct headers
        """
        # Given
        url = "https://fake-url.com"
        query_params = {"areaType": "Lower Tier Local Authority", "areaName": "London"}

        # When
        frontend_crawler_with_mocked_internal_api_client.hit_frontend_page(
            url=url, params=query_params
        )

        # Then
        expected_cdn_auth_key = (
            f'"{frontend_crawler_with_mocked_internal_api_client._cdn_auth_key}"'
        )
        spy_requests.get.assert_called_once_with(
            url=url,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            headers={"x-cdn-auth": expected_cdn_auth_key},
            params=query_params,
        )

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_geography_page_combination(
        self,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a page slug and an enriched `GeographyData` model
        When `process_geography_page_combination()` is called
            from an instance of the `FrontEndCrawler`
        Then the call is delegated to the `hit_frontend_page()` method
            with the correct URL and query parameters dict

        Patches:
            `spy_hit_frontend_page`: For the main assertion

        """
        # Given
        full_url = f"{frontend_crawler_with_mocked_internal_api_client._frontend_base_url}/topics/covid-19"
        mocked_page = mock.Mock(full_url=full_url)

        geography_data = GeographyData(
            name="London", geography_type_name="Lower Tier Local Authority"
        )

        # When
        frontend_crawler_with_mocked_internal_api_client.process_geography_page_combination(
            geography_data=geography_data,
            page=mocked_page,
        )

        # Then
        expected_params = {
            "areaType": "Lower+Tier+Local+Authority",
            "areaName": "London",
        }
        spy_hit_frontend_page.assert_called_once_with(
            url=full_url,
            params=expected_params,
        )

    @mock.patch(f"{MODULE_PATH}.call_with_star_map_multithreading")
    def test_process_geography_page_combinations(
        self,
        spy_call_with_star_map_multithreading: mock.MagicMock,
    ):
        """
        Given a `GeographiesAPICrawler` which returns
            a list of enriched `GeographyData` models
        When `process_geography_page_combinations()` is called
            from an instance of the `FrontEndCrawler`
        Then the call is delegated to `call_with_star_map_multithreading()`
            with the correct arguments

        Patches:
            `spy_call_with_star_map_multithreading`: For the main assertion

        """
        # Given
        geography_combinations = [
            GeographyData(
                name="London", geography_type_name="Lower Tier Local Authority"
            ),
            GeographyData(name="England", geography_type_name="Nation"),
        ]
        mocked_page = mock.Mock()
        mocked_geographies_api_crawler = mock.Mock()
        mocked_geographies_api_crawler.get_geography_combinations_for_page.return_value = (
            geography_combinations
        )
        frontend_crawler = FrontEndCrawler(
            geographies_api_crawler=mocked_geographies_api_crawler,
            frontend_base_url=mock.Mock(),
            cdn_auth_key=mock.Mock(),
        )

        # When
        frontend_crawler.process_geography_page_combinations(page=mocked_page)

        # Then
        mocked_geographies_api_crawler.get_geography_combinations_for_page.assert_called_once_with(
            page=mocked_page
        )

        expected_args = [
            (geography_data, mocked_page) for geography_data in geography_combinations
        ]
        spy_call_with_star_map_multithreading.assert_called_once_with(
            func=frontend_crawler.process_geography_page_combination,
            items=expected_args,
            thread_count=100,
        )

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    def test_process_geography_page_combination_logs_for_failed_request(
        self,
        mocked_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
        caplog: LogCaptureFixture,
    ):
        """
        Given a page slug and an enriched `GeographyData` model
        When `process_geography_page_combination()` is called
            from an instance of the `FrontEndCrawler`
        Then the call is delegated to the `hit_frontend_page()` method
            with the correct URL and query parameters dict

        Patches:
            `mocked_hit_frontend_page`: To simulate
                a flaky network request error

        """
        # Given
        full_url = f"{frontend_crawler_with_mocked_internal_api_client._frontend_base_url}/topics/covid-19"
        mocked_page = mock.Mock(full_url=full_url)
        geography_data = GeographyData(name="London", geography_type_name="Nation")
        mocked_hit_frontend_page.side_effect = ChunkedEncodingError

        # When
        frontend_crawler_with_mocked_internal_api_client.process_geography_page_combination(
            geography_data=geography_data,
            page=mocked_page,
        )

        # Then
        expected_params = {
            "areaType": "Nation",
            "areaName": "London",
        }

        expected_log = (
            f"`{full_url}` with params of `{expected_params}` could not be hit"
        )
        assert expected_log in caplog.text

    @mock.patch.object(FrontEndCrawler, "process_geography_page_combinations")
    @mock.patch(f"{MODULE_PATH}.get_pages_for_area_selector")
    def test_process_all_valid_area_selector_pages(
        self,
        spy_get_pages_for_area_selector: mock.MagicMock,
        spy_process_geography_page_combinations: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given `get_pages_for_area_selector()`
            which returns a list of pages
        When `process_all_valid_area_selector_pages()` is called
            from an instance of the `FrontEndCrawler`
        Then the `process_geography_page_combinations()` method
            is called for each page

        Patches:
            `spy_get_pages_for_area_selector`: To remove the
                side effect of having to hit the db
                to fetch area selector-enabled pages
            `spy_process_geography_page_combinations`: For the
                main assertion, checking each page was sent
                for processing

        """
        # Given
        mocked_pages = [mock.Mock()] * 3
        spy_get_pages_for_area_selector.return_value = mocked_pages

        # When
        frontend_crawler_with_mocked_internal_api_client.process_all_valid_area_selector_pages()

        # Then
        spy_get_pages_for_area_selector.assert_called_once()

        expected_calls = [mock.call(page=mocked_page) for mocked_page in mocked_pages]
        spy_process_geography_page_combinations.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    # Sitemap

    def test_sitemap_url(
        self,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a base URL
        When the `sitemap_url` property is called
            from an instance of the `FrontEndCrawler`
        Then the correct URL is returned
        """
        # Given
        base_url = frontend_crawler_with_mocked_internal_api_client._frontend_base_url

        # When
        sitemap_url: str = frontend_crawler_with_mocked_internal_api_client.sitemap_url

        # When
        assert sitemap_url == f"{base_url}/sitemap.xml"

    @mock.patch.object(FrontEndCrawler, "_hit_sitemap_url")
    def test_parse_sitemap(
        self,
        mocked_hit_sitemap_url: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given fake sitemap XML content
        When `_parse_sitemap()` is called
            from an instance of the `FrontEndCrawler`
        Then the sitemap is parsed correctly and returned
        """
        # Given
        mocked_response = mock.Mock()
        mocked_response.content = b"<?xml version='1.0' encoding='UTF-8'?><urlset><url><loc>https://example.com/</loc></url></urlset>"
        mocked_hit_sitemap_url.return_value = mocked_response

        # When
        parsed_sitemap_root = (
            frontend_crawler_with_mocked_internal_api_client._parse_sitemap()
        )

        # Then
        assert parsed_sitemap_root.tag == "urlset"
        assert parsed_sitemap_root.find("url/loc").text == "https://example.com/"

    @mock.patch.object(FrontEndCrawler, "_parse_sitemap")
    def test_traverse_sitemap(
        self,
        mocked_parse_sitemap: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a fake sitemap
        When `_traverse_sitemap()` is called
            from an instance of the `FrontEndCrawler`
        Then the correct URLs are extracted from the sitemap
        """
        # Given
        fake_sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>https://test.ukhsa-dashboard.data.gov.uk/</loc>
                <lastmod>2024-10-17T15:16:05.287Z</lastmod>
                <changefreq>monthly</changefreq>
                <priority>0.5</priority>
            </url>
            <url>
                <loc>https://test.ukhsa-dashboard.data.gov.uk/about/</loc>
                <lastmod>2024-10-17T15:16:05.288Z</lastmod>
                <changefreq>monthly</changefreq>
                <priority>0.5</priority>
            </url>
        </urlset>
        """
        parsed_sitemap = ElementTree.fromstring(fake_sitemap_content)
        mocked_parse_sitemap.return_value = parsed_sitemap

        # When
        extracted_urls: Iterator[str] = (
            frontend_crawler_with_mocked_internal_api_client._traverse_sitemap()
        )

        # Then
        expected_urls: set[str] = {
            "https://test.ukhsa-dashboard.data.gov.uk/",
            "https://test.ukhsa-dashboard.data.gov.uk/about/",
        }
        assert set(extracted_urls) == expected_urls

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_sitemap_url_returns_sitemap_xml(
        self,
        spy_requests: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a base URL
        When the `_hit_sitemap_url` method is called
            from an instance of the `FrontEndCrawler`
        Then a GET request is made to the correct URL
        """
        # Given
        base_url = frontend_crawler_with_mocked_internal_api_client._frontend_base_url

        # When
        response = frontend_crawler_with_mocked_internal_api_client._hit_sitemap_url()

        # When
        assert response == spy_requests.get.return_value
        expected_url = f"{base_url}/sitemap.xml"
        spy_requests.get.assert_called_once_with(url=expected_url, timeout=60)

    @mock.patch.object(FrontEndCrawler, "hit_frontend_page")
    @mock.patch.object(FrontEndCrawler, "_traverse_sitemap")
    def test_process_all_page_urls(
        self,
        mocked_traverse_sitemap: mock.MagicMock,
        spy_hit_frontend_page: mock.MagicMock,
        frontend_crawler_with_mocked_internal_api_client: FrontEndCrawler,
    ):
        """
        Given a generator of URLs to be traversed
        When `process_all_page_urls()` is called
            from an instance of the `FrontEndCrawler`
        Then the call is delegated to `hit_frontend_page()`
            for each URL
        """
        # Given
        traversed_urls: Iterator[str] = (
            x for x in ("https://abc.com", "https://def.com", "https://ghi.com")
        )
        mocked_traverse_sitemap.return_value = traversed_urls

        # When
        frontend_crawler_with_mocked_internal_api_client.process_all_page_urls()

        # Then
        expected_calls = [mock.call(url=url) for url in traversed_urls]
        spy_hit_frontend_page.assert_has_calls(calls=expected_calls)
