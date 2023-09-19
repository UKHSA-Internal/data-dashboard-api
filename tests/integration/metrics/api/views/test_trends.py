from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries, Topic


class TestTrendsView:
    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self,
        core_trend_percentage_example: list[CoreTimeSeries],
        core_headline_example: CoreTimeSeries,
    ):
        """
        Given the names of a `topic`, `metric` and `percentage_metric`
        When the `GET /api/trends/v2/` endpoint is hit
        Then an HTTP 200 OK response is returned with the correct trend data
        """
        # Given
        client = APIClient()
        main_record, percentage_record = core_trend_percentage_example
        topic_name = main_record.metric.metric_group.topic.name
        metric_name = main_record.metric.name
        percentage_metric_name = percentage_record.metric.name
        path = "/api/trends/v2/"

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
        assert response.status_code == HTTPStatus.OK
        expected_response_data = {
            "colour": "red",
            "direction": "up",
            "metric_name": metric_name,
            "metric_value": main_record.metric_value,
            "percentage_metric_name": percentage_metric_name,
            "percentage_metric_value": percentage_record.metric_value,
        }
        assert response.data == expected_response_data

    @pytest.mark.django_db
    def test_get_returns_error_message_for_timeseries_type_metric(
        self,
        core_trend_percentage_example: list[CoreTimeSeries],
    ):
        """
        Given the names of a `metric`, `percentage_metric` as well as an incorrect `topic`
        When the `GET /api/trends/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        main_record, percentage_record = core_trend_percentage_example
        metric_name = main_record.metric.name
        percentage_metric_name = percentage_record.metric.name

        # The `Topic` record needs to be available
        # Or else the serializer will invalidate the field choice first
        incorrect_topic_name = "Influenza"
        Topic.objects.create(name=incorrect_topic_name)
        path = "/api/trends/v2/"

        # When
        response: Response = client.get(
            path=path,
            data={
                "topic": incorrect_topic_name,
                "metric": metric_name,
                "percentage_metric": percentage_metric_name,
            },
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


class TestTrendsViewBeta:
    @property
    def path(self) -> str:
        return "/api/trends/v3/"

    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self,
        core_trend_example_beta: tuple[CoreHeadline, CoreHeadline],
    ):
        """
        Given the names of a `topic`, `metric` and `percentage_metric`
        When the `GET /api/trends/v3/` endpoint is hit
        Then an HTTP 200 OK response is returned with the correct trend data
        """
        # Given
        client = APIClient()
        main_record, percentage_record = core_trend_example_beta
        topic_name = main_record.metric.metric_group.topic.name
        metric_name = main_record.metric.name
        percentage_metric_name = percentage_record.metric.name

        # When
        response: Response = client.get(
            path=self.path,
            data={
                "topic": topic_name,
                "metric": metric_name,
                "percentage_metric": percentage_metric_name,
                "geography": main_record.geography.name,
                "geography_type": main_record.geography.geography_type.name,
            },
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        expected_response_data = {
            "colour": "red",
            "direction": "up",
            "metric_name": metric_name,
            "metric_value": main_record.metric_value,
            "percentage_metric_name": percentage_metric_name,
            "percentage_metric_value": percentage_record.metric_value,
        }
        assert response.data == expected_response_data
