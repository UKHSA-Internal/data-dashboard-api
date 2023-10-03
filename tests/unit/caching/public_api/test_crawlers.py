from unittest import mock

import pytest

from caching.public_api.crawler import PublicAPICrawler

MODULE_PATH = "caching.public_api.crawler"

FAKE_URL = "https://www.fake-api.com"


@pytest.fixture
def fake_public_api_crawler() -> PublicAPICrawler:
    return PublicAPICrawler(
        public_api_base_url=FAKE_URL,
        cdn_auth_key="abc",
    )


class TestPublicAPICrawler:
    def test_create_crawler_for_cache_refresh(self):
        """
        Given a public API url and a CDN auth key
        When the `create_crawler_for_cache_refresh()` class method is called
            from the `PublicAPICrawler` class
        Then the args are passed to the created instance of the `PublicAPICrawler`
        """
        # Given
        fake_public_api_base_url = "abc"
        fake_cdn_auth_key = "123"

        # When
        created_crawler = PublicAPICrawler.create_crawler_for_cache_refresh(
            public_api_base_url=fake_public_api_base_url,
            cdn_auth_key=fake_cdn_auth_key,
        )

        # Then
        assert created_crawler._public_api_base_url == fake_public_api_base_url
        assert created_crawler._cdn_auth_key == fake_cdn_auth_key

    # Headers construction

    def test_build_base_headers(self):
        """
        Given a CDN auth key
        When `_build_base_headers()` is called
            from an instance of the `PublicAPICrawler`
        Then the returned headers contains the CDN auth key
        """
        # Given
        mocked_cdn_auth_key = mock.Mock()
        crawler = PublicAPICrawler(
            public_api_base_url=mock.Mock(), cdn_auth_key=mocked_cdn_auth_key
        )

        # When
        base_headers: dict[str, str] = crawler._build_base_headers()

        # Then
        assert base_headers["x-cdn-auth"] == mocked_cdn_auth_key

    def test_build_headers_for_html(self):
        """
        Given a CDN auth key
        When `build_headers_for_html()` is called
            from an instance of the `PublicAPICrawler`
        Then the returned headers contains the CDN auth key
        And the correct "Accept" header
        """
        # Given
        mocked_cdn_auth_key = mock.Mock()
        crawler = PublicAPICrawler(
            public_api_base_url=mock.Mock(), cdn_auth_key=mocked_cdn_auth_key
        )

        # When
        constructed_headers: dict[str, str] = crawler.build_headers_for_html()

        # Then
        assert constructed_headers["x-cdn-auth"] == mocked_cdn_auth_key
        assert constructed_headers["Accept"] == "text/html"

    # Endpoint call methods

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_endpoint_for_json(
        self, spy_requests: mock.MagicMock, fake_public_api_crawler: PublicAPICrawler
    ):
        """
        Given a URL
        When `_hit_endpoint_for_json()` is called
            from an instance of the `PublicAPICrawler`
        Then a GET request is made with the correct args

        Patches:
            `spy_requests`: For the main assertion
        """
        # Given
        fake_url = FAKE_URL

        # When
        json_response = fake_public_api_crawler._hit_endpoint_for_json(url=fake_url)

        # Then
        spy_requests.get.assert_called_once_with(
            url=fake_url,
            timeout=fake_public_api_crawler._request_timeout,
            headers=fake_public_api_crawler._build_base_headers(),
        )
        assert json_response == spy_requests.get.return_value.json.return_value

    @mock.patch(f"{MODULE_PATH}.requests")
    def test_hit_endpoint_for_html(
        self, spy_requests: mock.MagicMock, fake_public_api_crawler: PublicAPICrawler
    ):
        """
        Given a URL
        When `_hit_endpoint_for_html()` is called
            from an instance of the `PublicAPICrawler`
        Then a GET request is made with the correct args

        Patches:
            `spy_requests`: For the main assertion
        """
        # Given
        fake_url = FAKE_URL

        # When
        json_response = fake_public_api_crawler._hit_endpoint_for_html(url=fake_url)

        # Then
        spy_requests.get.assert_called_once_with(
            url=fake_url,
            timeout=fake_public_api_crawler._request_timeout,
            headers=fake_public_api_crawler.build_headers_for_html(),
        )
        assert json_response == spy_requests.get.return_value.content

    @mock.patch.object(PublicAPICrawler, "_hit_endpoint_for_json")
    @mock.patch.object(PublicAPICrawler, "_hit_endpoint_for_html")
    def test_hit_endpoint(
        self,
        spy_hit_endpoint_for_html: mock.MagicMock,
        spy_hit_endpoint_for_json: mock.MagicMock,
        fake_public_api_crawler,
    ):
        """
        Given a URL
        When `hit_endpoint()` is called
            from an instance of the `PublicAPICrawler`
        Then the call is delegated to handle the different
            types of supported requests which are to be cached

        Patches:
            `spy_hit_endpoint_for_html`: To check the call
                for HTML requests are made
            `spy_hit_endpoint_for_json`: To check the call
                for JSON requests are made

        """
        # Given
        url = FAKE_URL

        # When
        endpoint_response = fake_public_api_crawler.hit_endpoint(url=url)

        # Then
        spy_hit_endpoint_for_html.assert_called_once_with(url=url)
        spy_hit_endpoint_for_json.assert_called_once_with(url=url)
        assert endpoint_response == spy_hit_endpoint_for_json.return_value

    # Recursive crawl

    @mock.patch.object(PublicAPICrawler, "get_links_from_response_data")
    @mock.patch.object(PublicAPICrawler, "hit_endpoint")
    def test_crawl(
        self,
        spy_hit_endpoint: mock.MagicMock,
        mocked_get_links_from_response_data: mock.MagicMock,
        fake_public_api_crawler: PublicAPICrawler,
    ):
        """
        Given a base root URL and a number of subsequent URLs
        When the recursive `crawl()` method is called
            from an instance of the `PublicAPICrawler`
        Then each URL is called in order

        Patches:
            `spy_hit_endpoint`: To check all URLs
                are processed properly
            `mocked_get_links_from_response_data`: To provide
                the fake response data to the test

        """
        # Given
        url = FAKE_URL
        subsequent_level_urls = [
            f"{FAKE_URL}/respiratory",
            f"{FAKE_URL}/respiratory/sub_themes",
        ]
        mocked_get_links_from_response_data.return_value = subsequent_level_urls

        # When
        fake_public_api_crawler.crawl(url=url, crawled_urls=[])

        # Then
        expected_urls_to_be_called = [url]
        expected_urls_to_be_called += subsequent_level_urls

        expected_calls = [mock.call(url=url) for url in expected_urls_to_be_called]
        # URLs should be traversed from top down hence the `any_order=False` flag
        spy_hit_endpoint.assert_has_calls(calls=expected_calls, any_order=False)

    def test_get_links_from_response_data(
        self, fake_public_api_crawler: PublicAPICrawler
    ):
        """
        Given response data which contains a valid link and an invalid value
        When `get_links_from_response_data()` is called
            from an instance of the `PublicAPICrawler`
        Then the correct link is returned
        """
        # Given
        valid_link = "https://example.com"
        invalid_value = "abc"
        response_data = [{"link": valid_link, "information": invalid_value}]

        # When
        extracted_links: list[
            str
        ] = fake_public_api_crawler.get_links_from_response_data(
            response_data=response_data
        )

        # Then
        assert valid_link in extracted_links
        assert invalid_value not in extracted_links

    # Processing API

    @mock.patch.object(PublicAPICrawler, "crawl")
    def test_crawl_public_api_themes_path(self, spy_crawl: mock.MagicMock):
        """
        Given a URL to crawl
        When `crawl_public_api_themes_path()` is called
            from an instance of the `PublicAPICrawler`
        Then the correct URL is passed to the `crawl()` method

        Patches:
            `spy_crawl`: For the main assertion,
                to check that the recursive `crawl` method is called
                for the correct initial root path
        """
        # Given
        base_url = FAKE_URL
        public_api_crawler = PublicAPICrawler(
            public_api_base_url=base_url, cdn_auth_key=mock.Mock()
        )

        # When
        public_api_crawler.crawl_public_api_themes_path()

        # Then
        expected_initial_root_path = f"{FAKE_URL}/themes/"
        spy_crawl.assert_called_once_with(
            url=expected_initial_root_path, crawled_urls=[]
        )

    @mock.patch.object(PublicAPICrawler, "crawl_public_api_themes_path")
    def test_process_all_routes(
        self,
        spy_crawl_public_api_themes_path: mock.MagicMock,
        fake_public_api_crawler: PublicAPICrawler,
    ):
        """
        Given no input arguments
        When `process_all_routes()` is called
            from an instance of the `PublicAPICrawler`
        Then a call is delegated to the `crawl_public_api_themes_path()`

        Patches:
            `spy_crawl_public_api_themes_path`: For the main assertion

        """
        # Given / When
        fake_public_api_crawler.process_all_routes()

        # Then
        spy_crawl_public_api_themes_path.assert_called_once()
