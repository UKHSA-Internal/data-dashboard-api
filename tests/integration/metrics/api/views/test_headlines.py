from http import HTTPStatus
from typing import List

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries


class TestHeadlinesView:
    @property
    def path(self) -> str:
        return "/headlines/v2/"

    @pytest.mark.parametrize("path", ["/headlines/v2/", "/api/headlines/v2/"])
    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_headline_example: CoreTimeSeries,
    ):
        """
        Given the names of a `metric` and `topic`
        And an authenticated APIClient
        When the `GET /headlines/v2/` endpoint is hit
        Then an HTTP 200 OK response is returned with the associated metric_value
        """
        # Given
        topic_name: str = core_headline_example.metric.topic.name
        metric_name: str = core_headline_example.metric.name

        # When
        response: Response = authenticated_api_client.get(
            path=path, data={"topic": topic_name, "metric": metric_name}
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"value": core_headline_example.metric_value}

    @pytest.mark.parametrize("path", ["/headlines/v2/", "/api/headlines/v2/"])
    @pytest.mark.django_db
    def test_get_returns_error_message_for_timeseries_type_metric(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: List[CoreTimeSeries],
    ):
        """
        Given a `topic` and a `metric` which has more than 1 record and is a timeseries type metric
        And an authenticated APIClient
        When the `GET /headlines/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned with the expected error message
        """
        # Given
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.topic.name
        metric_name: str = core_timeseries.metric.name

        # When
        response: Response = authenticated_api_client.get(
            path=path,
            data={"topic": topic_name, "metric": metric_name},
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        expected_error_message = f"`{metric_name}` is a timeseries-type metric. This should be a headline-type metric"
        assert response.data == {"error_message": expected_error_message}

    @pytest.mark.parametrize("path", ["/headlines/v2/", "/api/headlines/v2/"])
    @pytest.mark.django_db
    def test_get_request_without_api_key_is_unauthorized(self, path: str):
        """
        Given the names of a `metric` and `topic`
        And an APIClient which is not authenticated
        When the `GET /headlines/v2/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        metric_name = "COVID-19_headline_ONSdeaths_7daytotals"
        topic_name = "COVID-19"
        client = APIClient()

        # When
        response: Response = client.get(
            path=path, data={"topic": topic_name, "metric": metric_name}
        )

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
