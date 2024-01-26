from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreHeadline, Topic


class TestHeadlinesView:
    @property
    def path(self) -> str:
        return "/api/headlines/v3/"

    @pytest.mark.django_db
    def test_get_returns_correct_response(
        self,
        core_headline_example: CoreHeadline,
    ):
        """
        Given a valid payload for a `CoreHeadline` which exists
        When the `GET /api/headlines/v3/` endpoint is hit
        Then an HTTP 200 OK response is returned with the associated metric_value
        """
        # Given
        client = APIClient()
        payload = {
            "topic": core_headline_example.metric.metric_group.topic.name,
            "metric": core_headline_example.metric.name,
            "geography": core_headline_example.geography.name,
            "geography_type": core_headline_example.geography.geography_type.name,
        }

        # When
        response: Response = client.get(path=self.path, data=payload)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data == {"value": core_headline_example.metric_value}

    @pytest.mark.django_db
    def test_get_returns_error_for_invalid_request(
        self, core_headline_example: CoreHeadline
    ):
        """
        Given the name of a `metric` as well as an incorrect `topic`
        When the `GET /api/headlines/v3/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()

        # The `Topic` record needs to be available
        # Or else the serializer will invalidate the field choice first
        incorrect_topic_name = "Influenza"
        Topic.objects.create(name=incorrect_topic_name)

        # When
        response: Response = client.get(
            path=self.path,
            data={
                "topic": incorrect_topic_name,
                "metric": core_headline_example.metric.name,
                "geography": core_headline_example.geography.name,
                "geography_type": core_headline_example.geography.geography_type.name,
            },
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
