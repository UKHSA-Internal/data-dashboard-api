import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, Metric, Topic


class TestChartsView:
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
        return "/charts/v2/"

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /charts/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        path_without_trailing_forward_slash: str = self.path.strip("/")
        metric_name = "vaccinations_percentage_uptake_spring22"
        topic_name = "COVID-19"
        self._setup_core_time_series(
            metric_name=metric_name, metric_value=13, topic_name=topic_name
        )
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=path_without_trailing_forward_slash,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_returns_correct_response(self, authenticated_api_client: APIClient):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /charts/v2/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        metric_name = "vaccinations_percentage_uptake_spring22"
        topic_name = "COVID-19"
        self._setup_core_time_series(
            metric_name=metric_name, metric_value=13, topic_name=topic_name
        )
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate an `svg` image being returned
        assert response.headers["Content-Type"] == "image/svg+xml"

    @pytest.mark.django_db
    def test_post_request_without_api_key_is_unauthorized(self):
        """
        Given an APIClient which is not authenticated
        When the `GET /charts/v2/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.post(path=self.path, data={})

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
