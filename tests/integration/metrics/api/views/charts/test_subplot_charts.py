import random
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.charts.subplot_charts.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from metrics.data.models.core_models import CoreTimeSeries
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestSubplotChartsView:
    @staticmethod
    def _create_example_core_timeseries() -> list[CoreTimeSeries]:
        utla = "Upper Tier Local Authority"
        region = "Region"
        geographies = [
            ("Darlington", utla),
            ("Hartlepool", utla),
            ("Stockton-on-Tees", utla),
            ("North West", region),
            ("West Midlands", region),
            ("London", region),
        ]

        possible_metric_values = [0.9, 0.8, 0.76, 0.82, 0.99]

        core_time_series = []

        for geography in geographies:
            geography_name = geography[0]
            geography_type = geography[1]
            metric_value = random.choice(possible_metric_values)

            core_time_series.append(
                CoreTimeSeriesFactory.create_record(
                    theme_name="immunisation",
                    sub_theme_name="childhood-vaccines",
                    topic_name="MMR1",
                    metric_name="MMR1_coverage_coverageByYear",
                    stratum_name="24m",
                    date="2021-08-01",
                    geography_name=geography_name,
                    geography_type_name=geography_type,
                    metric_value=metric_value,
                )
            )
        return core_time_series

    @property
    def path(self) -> str:
        return "/api/charts/subplot/v1/"

    @pytest.mark.django_db
    def test_returns_correct_response_for_preview(self):
        """
        Given a valid payload to create a subplots chart
        When the `POST /api/charts/subplot/v1/` endpoint is hit
        Then the response is an HTTP 200 OK
            with the correct content-type of image/png
        """
        # Given
        client = APIClient()
        self._create_example_core_timeseries()
        valid_payload = REQUEST_PAYLOAD_EXAMPLE.copy()
        valid_payload["file_format"] = "png"

        # When
        response: Response = client.post(
            path=f"{self.path}?preview=true",
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK != HTTPStatus.UNAUTHORIZED

        # Check that the headers on the response indicate a `png` image being returned
        assert response.headers["Content-Type"] == "image/png"

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly_for_v3(
        self,
    ):
        """
        Given a valid payload to create a subplots chart
        When the `POST /api/charts/subplot/v1` endpoint is hit
            i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        core_time_series: list[CoreTimeSeries] = self._create_example_core_timeseries()
        valid_payload = REQUEST_PAYLOAD_EXAMPLE.copy()

        # When
        response: Response = client.post(
            path="/api/charts/subplot/v1",
            data=valid_payload,
            format="json",
        )

        # Then
        # Check that the headers on the response indicate a json response is being returned
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.django_db
    @pytest.mark.parametrize("preview", [True, False])
    def test_returns_bad_request_response_when_queried_data_does_not_exist(
        self, preview: bool
    ):
        """
        Given a payload for which there is no corresponding data
        When the `POST /api/charts/subplot/v1/` endpoint is hit
        Then the response is an HTTP 400 BAD REQUEST
        """
        # Given
        client = APIClient()
        # Note that the authentication is only needed for the v2 endpoint
        valid_payload = REQUEST_PAYLOAD_EXAMPLE
        path = f"{self.path}?preview={preview}"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
