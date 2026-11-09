from http import HTTPStatus
from unittest import mock

import pytest
from rest_framework.test import APIClient

import config
from metrics.interfaces.health.probes import HealthProbeManagement


class TestHealthView:
    @pytest.mark.parametrize("path", ["/health", "/health/"])
    def test_returns_200_ok(self, path: str):
        """
        Given an `APIClient`
        When a `GET` request is made to the `/health` endpoint
            with or without a trailing slash
        Then an HTTP 200 OK response is returned
            without being redirected
        """
        # Given
        client = APIClient()

        # When
        response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.OK.value

    @mock.patch.object(config, "COMMIT_SHA", "abc123")
    @mock.patch.object(config, "APP_VERSION", "1.2.3")
    def test_returns_status_version_and_commit_sha(self):
        """
        Given an `APIClient`
        And the `APP_VERSION` and `COMMIT_SHA` config values are set
        When a `GET` request is made to the `/health` endpoint
        Then the JSON response body contains
            the status, version and commit sha
        """
        # Given
        client = APIClient()

        # When
        response = client.get(path="/health")

        # Then
        assert response.json() == {
            "status": "OK",
            "version": "1.2.3",
            "commit_sha": "abc123",
        }


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
