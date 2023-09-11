from http import HTTPStatus
from unittest import mock

from rest_framework.test import APIClient

from caching.decorators import CacheCheckResultedInMissError

MODULE_PATH = "metrics.api.views.health"


class TestHealthView:
    @property
    def path(self) -> str:
        return "/health/"

    @mock.patch(f"{MODULE_PATH}.check_cache_for_all_pages")
    def test_returns_200_if_check_cache_for_all_pages_succeeds(
        self, spy_check_cache_for_all_pages: mock.MagicMock
    ):
        """
        Given the `check_cache_for_all_pages()` function
            which will run successfully
        When a `GET` request is made to the `/health/` endpoint
        Then an HTTP 200 OK response is returned

        Patches:
            `spy_check_cache_for_all_pages`: To simulate
                the cache being fully hydrated
        """
        # Given
        client = APIClient()
        spy_check_cache_for_all_pages.return_value = None

        # When
        response = client.get(path=self.path, data={"key": "value"})

        # Then
        assert response.status_code == HTTPStatus.OK.value

    @mock.patch(f"{MODULE_PATH}.check_cache_for_all_pages")
    def test_returns_503_if_check_cache_for_all_pages_fails_if_in_private_api_mode(
        self, spy_check_cache_for_all_pages: mock.MagicMock
    ):
        """
        Given the `check_cache_for_all_pages()` function
            which will raise a `CacheCheckResultedInMissError`
        When a `GET` request is made to the `/health/` endpoint
        Then an HTTP 503 SERVICE UNAVAILABLE response is returned

        Patches:
            `spy_check_cache_for_all_pages`: To simulate
                a cache miss occurring when checking the cache
        """
        # Given
        client = APIClient()
        spy_check_cache_for_all_pages.side_effect = CacheCheckResultedInMissError

        # When
        with mock.patch("config.APP_MODE", "PRIVATE_API"):
            response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE.value

    def test_post_returns_not_allowed(self):
        """
        Given an APIClient
        When a `POST` request is made to the `/health/` endpoint
        Then an HTTP 405 METHOD_NOT_ALLOWED response is returned
        """
        # Given
        client = APIClient()

        # When
        response = client.post(path="/health/")

        # Then
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
