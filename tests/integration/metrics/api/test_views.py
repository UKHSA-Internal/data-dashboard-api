from http import HTTPStatus

from rest_framework.test import APIClient


class TestHealthView:
    def test_returns_http_ok(self):
        """
        Given an APIClient
        When a `GET` request is made to the `/health/` endpoint
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()

        # When
        response = client.get("/health/")

        # Then
        assert response.status_code == HTTPStatus.OK
