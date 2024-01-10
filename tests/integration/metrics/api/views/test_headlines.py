from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreHeadline


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
