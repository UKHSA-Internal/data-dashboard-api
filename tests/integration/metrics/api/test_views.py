import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, Metric, Topic


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


@pytest.mark.django_db
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

    def test_get_returns_correct_response(self):
        """
        Given the names of a `metric` and `topic`
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

        client = APIClient()

        # When
        response: Response = client.get(
            path="/headlines/v2/", data={"topic": topic_name, "metric": metric_name}
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"value": metric_value}
