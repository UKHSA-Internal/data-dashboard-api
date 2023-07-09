from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries


class TestChartsView:
    @staticmethod
    def _build_valid_payload_for_existing_timeseries(core_timeseries: CoreTimeSeries):
        return {
            "file_format": "svg",
            "plots": [
                {
                    "topic": core_timeseries.metric.metric_group.topic.name,
                    "metric": core_timeseries.metric.name,
                    "chart_type": "waffle",
                }
            ],
        }

    @pytest.mark.parametrize("path", ["/charts/v2", "/api/charts/v2"])
    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /charts/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("path", ["/charts/v2/", "/api/charts/v2/"])
    @pytest.mark.django_db
    def test_returns_correct_response(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /charts/v2/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate an `svg` image being returned
        assert response.headers["Content-Type"] == "image/svg+xml"

    @pytest.mark.parametrize("path", ["/charts/v2/", "/api/charts/v2/"])
    @pytest.mark.django_db
    def test_post_request_without_api_key_is_unauthorized(self, path: str):
        """
        Given an APIClient which is not authenticated
        When the `GET /charts/v2/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.post(path=path, data={})

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize("path", ["/charts/v3", "/api/charts/v3"])
    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /charts/v3` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("path", ["/charts/v3/", "/api/charts/v3/"])
    @pytest.mark.django_db
    def test_returns_correct_response(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /charts/v3/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate a json response is being returned
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.parametrize("path", ["/charts/v3/", "/api/charts/v3/"])
    @pytest.mark.django_db
    def test_post_request_without_api_key_is_unauthorized(self, path: str):
        """
        Given an APIClient which is not authenticated
        When the `GET /charts/v3/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.post(path=path, data={})

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
