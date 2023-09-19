from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries


class TestHeadlinesView:
    @property
    def path(self) -> str:
        return "/headlines/v2/"

    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self,
        core_headline_example: CoreTimeSeries,
    ):
        """
        Given the names of a `metric` and `topic`
        When the `GET /api/headlines/v2/` endpoint is hit
        Then an HTTP 200 OK response is returned with the associated metric_value
        """
        # Given
        client = APIClient()
        topic_name: str = core_headline_example.metric.metric_group.topic.name
        metric_name: str = core_headline_example.metric.name
        path = "/api/headlines/v2/"

        # When
        response: Response = client.get(
            path=path, data={"topic": topic_name, "metric": metric_name}
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"value": core_headline_example.metric_value}

    @pytest.mark.django_db
    def test_get_returns_error_message_for_timeseries_type_metric(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a `topic` and a `metric` which has more than 1 record and is a timeseries type metric
        When the `GET /api/headlines/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        path = "/api/headlines/v2/"

        # When
        response: Response = client.get(
            path=path,
            data={"topic": topic_name, "metric": metric_name},
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestHeadlinesViewBeta:
    @property
    def path(self) -> str:
        return "/api/headlines/v3/"

    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self,
        core_headline_example_beta: CoreHeadline,
    ):
        """
        Given a valid payload for a `CoreHeadline` which exists
        When the `GET /api/headlines/v3/` endpoint is hit
        Then an HTTP 200 OK response is returned with the associated metric_value
        """
        # Given
        client = APIClient()
        payload = {
            "topic": core_headline_example_beta.metric.metric_group.topic.name,
            "metric": core_headline_example_beta.metric.name,
            "geography": core_headline_example_beta.geography.name,
            "geography_type": core_headline_example_beta.geography.geography_type.name,
        }

        # When
        response: Response = client.get(path=self.path, data=payload)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"value": core_headline_example_beta.metric_value}
