import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, Metric, Topic


class TestHeadlinesView:
    @staticmethod
    def _setup_core_time_series(
        topic_name: str, metric_name: str, metric_value: float
    ) -> CoreTimeSeries:
        topic = Topic.objects.create(name=topic_name)
        metric = Metric.objects.create(name=metric_name, topic=topic)
        year = 2023
        return CoreTimeSeries.objects.create(
            metric_value=metric_value,
            metric=metric,
            year=year,
            epiweek=1,
            dt=datetime.date(year=year, month=1, day=1),
        )

    @property
    def path(self) -> str:
        return "/headlines/v2/"

    @pytest.mark.parametrize("path", ["/headlines/v2/", "/api/headlines/v2/"])
    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given the names of a `metric` and `topic`
        And an authenticated APIClient
        When the `GET /headlines/v2/` endpoint is hit
        Then an HTTP 200 OK response is returned with the associated metric_value
        """
        # Given
        metric_name = "new_cases_7days_sum"
        topic_name = "COVID-19"
        metric_value = 123
        self._setup_core_time_series(
            topic_name=topic_name, metric_name=metric_name, metric_value=metric_value
        )

        # When
        response: Response = authenticated_api_client.get(
            path=path, data={"topic": topic_name, "metric": metric_name}
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"value": metric_value}

    @pytest.mark.parametrize("path", ["/headlines/v2/", "/api/headlines/v2/"])
    @pytest.mark.django_db
    def test_get_returns_error_message_for_timeseries_type_metric(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given a `topic` and a `metric` which has more than 1 record and is a timeseries type metric
        And an authenticated APIClient
        When the `GET /headlines/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned with the expected error message
        """
        # Given
        incorrect_metric_name = "COVID-19_deaths_ONSByDay"
        topic_name = "COVID-19"
        metric_value = 123

        # Create multiple records to emulate time-series type data
        for _ in range(2):
            self._setup_core_time_series(
                topic_name=topic_name,
                metric_name=incorrect_metric_name,
                metric_value=metric_value,
            )

        # When
        response: Response = authenticated_api_client.get(
            path=path,
            data={"topic": topic_name, "metric": incorrect_metric_name},
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        expected_error_message = f"`{incorrect_metric_name}` is a timeseries-type metric. This should be a headline-type metric"
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
        metric_name = "new_cases_7days_sum"
        topic_name = "COVID-19"
        client = APIClient()

        # When
        response: Response = client.get(
            path=path, data={"topic": topic_name, "metric": metric_name}
        )

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
