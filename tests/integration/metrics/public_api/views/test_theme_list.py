import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.api_models import APITimeSeries


class TestThemeListView:
    @property
    def path(self) -> str:
        return "/api/public/timeseries/themes/"

    @property
    def test_server_base_name(self) -> str:
        return "http://testserver"

    @staticmethod
    def _setup_api_time_series(
        **kwargs,
    ) -> APITimeSeries:
        return APITimeSeries.objects.create(
            metric_value=123,
            epiweek=1,
            year=2023,
            dt=datetime.date(year=2023, month=1, day=1),
            **kwargs,
        )

    @pytest.mark.django_db
    def test_returns_correct_response(self, client: APIClient):
        """
        Given a valid request
        When the `GET /api/public/timeseries/themes/` endpoint is hit
        Then the response is an HTTP 200 OK
        And the response contains a list of theme names and links
        """
        # Given
        theme_value = "infectious_disease"
        self._setup_api_time_series(theme=theme_value)

        # When
        response: Response = client.get(path=self.path, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK

        response_data = response.data
        # Check that each object in the response contains a name and link
        assert response_data[0]["name"] == theme_value
        expected_theme_link = f"{self.test_server_base_name}{self.path}{theme_value}"
        assert response_data[0]["link"] == expected_theme_link
