from http import HTTPStatus

from rest_framework.test import APIClient


class TestHealthView:
    def test_get_returns_http_ok(self):
        """
        Given an APIClient
        When a `GET` request is made to the `/health/` endpoint
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()

        # When
        response = client.get(path="/health/")

        # Then
        assert response.status_code == HTTPStatus.OK

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
