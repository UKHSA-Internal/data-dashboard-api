from http import HTTPStatus
from unittest import mock

from rest_framework.test import APIClient

from metrics.interfaces.health.probes import HealthProbeManagement


class TestHealthView:
    @property
    def path(self) -> str:
        return "/health/"

    def test_returns_200_ok(self):
        """
        Given an `APIClient`
        When a `GET` request is made to the `/health/` endpoint
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()

        # When
        response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.OK.value


class TestInternalHealthView:
    @property
    def path(self) -> str:
        return "/.well-known/health-check/"

    @mock.patch.object(HealthProbeManagement, "perform_health_check")
    def test_returns_200_if_healthy(self, mocked_perform_health_check: mock.MagicMock):
        """
        Given an `APIClient`
        And the underlying health probe which returns True
            indicating a healthy probe
        When a `GET` request is made
            to the `/.well-known/health-check/` endpoint
        Then an HTTP 200 OK response is returned
        """
        # Given
        mocked_perform_health_check.return_value = True
        client = APIClient()

        # When
        response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.OK.value

    @mock.patch.object(HealthProbeManagement, "perform_health_check")
    def test_returns_503_if_unhealthy(
        self, mocked_perform_health_check: mock.MagicMock
    ):
        """
        Given an `APIClient`
        And the underlying health probe which returns False
            indicating an unhealthy probe
        When a `GET` request is made
            to the /.well-known/health-check/` endpoint
        Then an HTTP 503 SERVICE UNAVAILABLE response is returned
        """
        # Given
        mocked_perform_health_check.return_value = False
        client = APIClient()

        # When
        response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE.value
