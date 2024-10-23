from unittest import mock

import pytest

from caching.frontend.crawler import FrontEndCrawler
from caching.frontend.handlers import (
    FrontEndURLNotProvidedError,
    _get_frontend_base_url,
    crawl_front_end,
)


class TestGetFrontendBaseURL:
    def test_returns_correct_environment_variable_value(self, monkeypatch):
        """
        Given a value set for the environment variable "FRONTEND_URL"
        When `_get_frontend_base_url()` is called
        Then the correct value is returned
        """
        # Given
        fake_front_end_base_url = "https://www.fake-url.com"
        monkeypatch.setenv(name="FRONTEND_URL", value=fake_front_end_base_url)

        # When
        retrieved_frontend_base_url: str = _get_frontend_base_url()

        # Then
        assert retrieved_frontend_base_url == fake_front_end_base_url

    def test_raises_error_when_environment_variable_does_not_exist(self, monkeypatch):
        """
        Given no value set for the environment variable "FRONTEND_URL"
        When `_get_frontend_base_url()` is called
        Then a `FrontEndURLNotProvidedError` is raised
        """
        # Given
        monkeypatch.delenv(name="FRONTEND_URL", raising=False)

        # When / Then
        with pytest.raises(FrontEndURLNotProvidedError):
            _get_frontend_base_url()


class TestCrawlFrontEnd:
    @mock.patch.object(FrontEndCrawler, "process_all_valid_area_selector_pages")
    @mock.patch.object(FrontEndCrawler, "process_all_page_urls")
    def test_delegates_call_to_frontend_crawler(
        self,
        spy_process_all_page_urls: mock.MagicMock,
        spy_process_all_valid_area_selector_pages: mock.MagicMock,
        monkeypatch,
    ):
        """
        Given `FRONTEND_URL` & `CDN_AUTH_KEY` environment variables
        When `crawl_front_end()` is called
        Then `process_all_pages()` is called from an instance of `FrontEndCrawler`

        Patches:
            `spy_process_all_page_urls`: For the main assertion
            `spy_process_all_valid_area_selector_pages`: For the main assertion

        """
        # Given
        monkeypatch.setenv("FRONTEND_URL", "fake-url")
        monkeypatch.setenv("CDN_AUTH_KEY", "fake-cdn-auth-key")

        # When
        crawl_front_end()

        # Then
        spy_process_all_page_urls.assert_called_once()
        spy_process_all_valid_area_selector_pages.assert_called_once()
