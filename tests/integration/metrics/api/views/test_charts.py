from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries


class TestChartsView:
    @staticmethod
    def _build_valid_payload_for_existing_timeseries(core_timeseries: CoreTimeSeries):
        return {
            "file_format": "svg",
            "plots": [
                {
                    "topic": core_timeseries.metric.metric_group.topic.name,
                    "metric": core_timeseries.metric.name,
                    "chart_type": "bar",
                }
            ],
        }

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly_for_v2(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/charts/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        path = "/api/charts/v2"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_returns_correct_response_for_v2(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/charts/v2/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        path = "/api/charts/v2/"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK != HTTPStatus.UNAUTHORIZED

        # Check that the headers on the response indicate an `svg` image being returned
        assert response.headers["Content-Type"] == "image/svg+xml"

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly_for_v3(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/charts/v3` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        path = "/api/charts/v3"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        response_data = response.data
        latest_date = max(
            core_timeseries.date for core_timeseries in core_timeseries_example
        )
        assert response_data["last_updated"] == str(latest_date)

    @pytest.mark.django_db
    def test_returns_correct_response_for_v3_age_based_chart(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create an age-based chart
        When the `POST /api/charts/v3/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        And the `last_updated` field is returned with the correct value
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        valid_payload["x_axis"] = "age"
        path = "/api/charts/v3/"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK != HTTPStatus.UNAUTHORIZED

        # Check that the headers on the response indicate a json response is being returned
        assert response.headers["Content-Type"] == "application/json"

        # Check that the "last_updated" is returned correctly for the age-based chart
        response_data = response.data
        latest_date = max(
            core_timeseries.date for core_timeseries in core_timeseries_example
        )
        assert response_data["last_updated"] == str(latest_date)
