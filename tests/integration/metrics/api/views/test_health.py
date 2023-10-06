from http import HTTPStatus

from rest_framework.test import APIClient

MODULE_PATH = "metrics.api.views.health"


class TestHealthView:
    @property
    def path(self) -> str:
        return "/health/"

    def test_returns_200_if_check_cache_for_all_pages_succeeds(self):
        """
        Given the `check_cache_for_all_pages()` function
            which will run successfully
        When a `GET` request is made to the `/health/` endpoint
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()

        # When
        response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.OK.value

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
