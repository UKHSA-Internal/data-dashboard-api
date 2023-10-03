from unittest import mock

import pytest

from caching.public_api.crawler import PublicAPICrawler
from caching.public_api.handlers import (
    _get_public_api_url,
    crawl_public_api,
    get_cdn_auth_key,
)

MODULE_PATH = "caching.public_api.handlers"


class TestCrawlPublicAPI:
    @mock.patch(f"{MODULE_PATH}._get_public_api_url")
    @mock.patch(f"{MODULE_PATH}.get_cdn_auth_key")
    @mock.patch.object(PublicAPICrawler, "create_crawler_for_cache_refresh")
    def test_initializes_public_api_crawler(
        self,
        spy_create_crawler_for_cache_refresh: mock.MagicMock,
        spy_get_cdn_auth_key: mock.MagicMock,
        spy_get_public_api_url: mock.MagicMock,
        monkeypatch,
    ):
        """
        Given no input
        When `crawl_public_api()` is called
        Then `create_crawler_for_cache_refresh()` is called
            from the `Crawler` class with the correct args

        Patches:
            `spy_create_crawler_for_cache_refresh`: For the main assertion
            `spy_get_cdn_auth_key`: To check the CDN auth key
                is used when creating the crawler
            `spy_get_public_api_url`: To check the public API URL
                is used when creating the crawler

        """
        # Given / When
        crawl_public_api()

        # Then
        expected_public_api_url_value = spy_get_public_api_url.return_value
        expected_cdn_auth_key_value = spy_get_cdn_auth_key.return_value

        spy_create_crawler_for_cache_refresh.assert_called_once_with(
            public_api_base_url=expected_public_api_url_value,
            cdn_auth_key=expected_cdn_auth_key_value,
        )

    @mock.patch.object(PublicAPICrawler, "process_all_routes")
    def test_delegates_call_to_public_api_crawler(
        self, spy_process_all_routes: mock.MagicMock, monkeypatch
    ):
        """
        Given environment variables set for "PUBLIC_API_URL" and "CDN_AUTH_KEY"
        When `crawl_public_api()` is called
        Then `process_all_routes()` is called
            from an instance of the `Crawler`

        Patches:
            `spy_process_all_routes`: For the main assertion

        """
        # Given
        monkeypatch.setenv("PUBLIC_API_URL", "")
        monkeypatch.setenv("CDN_AUTH_KEY", "")

        # When
        crawl_public_api()

        # Then
        spy_process_all_routes.assert_called_once()


class TestGetPublicAPIURL:
    def test_returns_correct_environment_variable_value(self, monkeypatch):
        """
        Given a value set for the environment variable "PUBLIC_API_URL"
        When `_get_public_api_url()` is called
        Then the correct value is returned
        """
        # Given
        fake_public_api_url_value = "https://www.fake-url.com"
        monkeypatch.setenv(name="PUBLIC_API_URL", value=fake_public_api_url_value)

        # When
        retrieved_public_api_url: str = _get_public_api_url()

        # Then
        assert retrieved_public_api_url == fake_public_api_url_value

    def test_raises_error_when_environment_variable_does_not_exist(self, monkeypatch):
        """
        Given no value set for the environment variable "PUBLIC_API_URL"
        When `_get_public_api_url()` is called
        Then a `KeyError` is raised
        """
        # Given
        monkeypatch.delenv(name="PUBLIC_API_URL", raising=False)

        # When / Then
        with pytest.raises(KeyError):
            _get_public_api_url()


class TestGetCDNAuthKey:
    def test_returns_correct_environment_variable_value(self, monkeypatch):
        """
        Given a value set for the environment variable "CDN_AUTH_KEY"
        When `get_cdn_auth_key()` is called
        Then the correct value is returned
        """
        # Given
        fake_cdn_auth_key_value = "abcdefghikj"
        monkeypatch.setenv(name="CDN_AUTH_KEY", value=fake_cdn_auth_key_value)

        # When
        retrieved_cdn_auth_key: str = get_cdn_auth_key()

        # Then
        assert retrieved_cdn_auth_key == f'"{fake_cdn_auth_key_value}"'

    def test_raises_error_when_environment_variable_does_not_exist(self, monkeypatch):
        """
        Given no value set for the environment variable "CDN_AUTH_KEY"
        When `get_cdn_auth_key()` is called
        Then a `KeyError` is raised
        """
        # Given
        monkeypatch.delenv(name="CDN_AUTH_KEY", raising=False)

        # When / Then
        with pytest.raises(KeyError):
            get_cdn_auth_key()
