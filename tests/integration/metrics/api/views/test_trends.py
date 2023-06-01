import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, Metric, Topic


class TestTrendsView:
    @staticmethod
    def _setup_core_time_series(
        topic_name: str,
        metric_name: str,
        metric_value: float,
        percentage_metric_name: str,
        percentage_metric_value: float,
    ) -> CoreTimeSeries:
        year = 2023
        date = datetime.date(year=year, month=1, day=1)

        topic = Topic.objects.create(name=topic_name)
        metric = Metric.objects.create(name=metric_name, topic=topic)
        percentage_metric = Metric.objects.create(
            name=percentage_metric_name, topic=topic
        )

        CoreTimeSeries.objects.create(
            metric_value=metric_value,
            metric=metric,
            year=year,
            epiweek=1,
            dt=date,
        )
        CoreTimeSeries.objects.create(
            metric_value=percentage_metric_value,
            metric=percentage_metric,
            year=year,
            epiweek=1,
            dt=date,
        )

    @pytest.mark.parametrize("path", ["/trends/v2/", "/api/trends/v2/"])
    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given the names of a `topic`, `metric` and `percentage_metric`
        And an authenticated APIClient
        When the `GET /trends/v2/` endpoint is hit
        Then an HTTP 200 OK response is returned with the correct trend data
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "new_deaths_7days_change"
        metric_value = 123
        percentage_metric_name = "new_deaths_7days_change_percentage"
        percentage_metric_value = 1.3

        # Create the records for the data which is expected to be returned
        self._setup_core_time_series(
            topic_name=topic_name,
            metric_name=metric_name,
            metric_value=metric_value,
            percentage_metric_name=percentage_metric_name,
            percentage_metric_value=percentage_metric_value,
        )

        # Create records for data which should be filtered out and not returned
        self._setup_core_time_series(
            topic_name="Influenza",
            metric_name="weekly_positivity_change",
            metric_value=-100,
            percentage_metric_name="weekly_percent_change_positivity",
            percentage_metric_value=-3.22,
        )

        # When
        response: Response = authenticated_api_client.get(
            path=path,
            data={
                "topic": topic_name,
                "metric": metric_name,
                "percentage_metric": percentage_metric_name,
            },
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        expected_response_data = {
            "colour": "red",
            "direction": "up",
            "metric_name": metric_name,
            "metric_value": metric_value,
            "percentage_metric_name": percentage_metric_name,
            "percentage_metric_value": percentage_metric_value,
        }
        assert response.data == expected_response_data

    @pytest.mark.parametrize("path", ["/trends/v2/", "/api/trends/v2/"])
    @pytest.mark.django_db
    def test_get_returns_error_message_for_timeseries_type_metric(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given the names of a `metric`, `percentage_metric` as well as an incorrect `topic`
        And an authenticated APIClient
        When the `GET /trends/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned with the expected error message
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "new_deaths_7days_change"
        percentage_metric_name = "new_deaths_7days_change_percentage"
        self._setup_core_time_series(
            topic_name=topic_name,
            metric_name=metric_name,
            metric_value=123,
            percentage_metric_name=percentage_metric_name,
            percentage_metric_value=1.3,
        )

        # The `Topic` record needs to be available
        # Or else the serializer will invalidate the field choice first
        incorrect_topic_name = "Influenza"
        Topic.objects.create(name=incorrect_topic_name)

        # When
        response: Response = authenticated_api_client.get(
            path=path,
            data={
                "topic": incorrect_topic_name,
                "metric": metric_name,
                "percentage_metric": percentage_metric_name,
            },
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        expected_error_message = (
            f"Data for `{incorrect_topic_name}` and `{metric_name}` could not be found."
        )
        assert response.data == {"error_message": expected_error_message}

    @pytest.mark.parametrize("path", ["/trends/v2/", "/api/trends/v2/"])
    @pytest.mark.django_db
    def test_get_request_without_api_key_is_unauthorized(self, path: str):
        """
        Given the names of a `topic`, `metric` and `percentage_metric`
        And an APIClient which is not authenticated
        When the `GET /trends/v2/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        topic_name = "COVID-19"
        metric_name = "new_deaths_7days_change"
        percentage_metric_name = "new_deaths_7days_change_percentage"
        client = APIClient()

        # When
        response: Response = client.get(
            path=path,
            data={
                "topic": topic_name,
                "metric": metric_name,
                "percentage_metric": percentage_metric_name,
            },
        )

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
