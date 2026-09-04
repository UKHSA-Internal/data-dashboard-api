import copy
import random
from xml.etree import ElementTree as ET
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
        core_time_series.append(
            CoreTimeSeriesFactory.create_record(
                theme_name="immunisation",
                sub_theme_name="childhood-vaccines",
                topic_name="MMR1",
                metric_name="OFF-SENS_MMR1_coverage_coverageByYear",
                stratum_name="24m",
                date="2021-08-01",
                geography_name="Scotland",
                geography_type_name="Nation",
                metric_value=90,
                is_public=False,
            )
        )
        return core_time_series

    @staticmethod
    def get_text_from_svg_response(response: Response) -> list[str]:
        svg = response.getvalue().decode(response.charset)
        return [
            " ".join(ET.tostringlist(text, encoding="unicode", method="text"))
            for text in ET.fromstring(svg).findall(".//{*}text")
        ]

    @property
    def path(self) -> str:
        return "/api/charts/subplot/v1/"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("authenticated_user"),
        [
            (True),
            (False),
        ],
    )
    def test_returns_correct_response_for_preview(
        self, authenticated_user, user_global_access
    ):
        """
        Given a valid payload to create a subplots chart
        When the `POST /api/charts/subplot/v1/` endpoint is hit
        Then the response is an HTTP 200 OK
            with the correct content-type of image/png
        """
        # Given
        client = APIClient()

        example_timeseries = self._create_example_core_timeseries()
        valid_payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)

        if authenticated_user:
            client.force_authenticate(user=user_global_access, token="token")
            valid_payload["subplots"].append(
                {
                    "subplot_title": "OFF SENS MMR1 (24 months)",
                    "subplot_parameters": {
                        "topic": "MMR1",
                        "metric": "OFF-SENS_MMR1_coverage_coverageByYear",
                        "stratum": "24m",
                    },
                    "plots": [
                        {
                            "label": "Scotland",
                            "geography": "Scotland",
                            "geography_type": "Nation",
                            "line_colour": "COLOUR_4_ORANGE",
                        },
                    ],
                }
            )

        expected_metrics = [ts.metric for ts in example_timeseries]
        expected_titles = [
            subplot["subplot_title"]
            for subplot in valid_payload["subplots"]
            if subplot["subplot_parameters"]["metric"] in expected_metrics
        ]

        # When
        response: Response = client.post(
            path=f"{self.path}?preview=true",
            data=valid_payload,
            format="json",
        )

        svg_text = self.get_text_from_svg_response(response)

        # Then
        assert response.status_code == HTTPStatus.OK != HTTPStatus.UNAUTHORIZED

        # Check that the headers on the response indicate a `svg` image being returned
        assert response.headers["Content-Type"] == "image/svg"

        # Check that the chart contains the expected plots
        for expected_title in expected_titles:
            assert expected_title in svg_text

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
        self._create_example_core_timeseries()
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
        response_data = response.data
        assert response_data["last_updated"] == "2021-08-01"

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
