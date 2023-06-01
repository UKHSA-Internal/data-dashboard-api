import csv
import io
from collections import OrderedDict
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.api_models import APITimeSeries


class TestDownloadsView:
    metric = "new_deaths_7day_avg"
    stratum = "default"
    api_timeseries_data = {
        "period": "D",
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "Nation",
        "geography": "England",
        "metric": metric,
        "stratum": stratum,
        "sex": "M",
        "year": 2023,
        "epiweek": 1,
        "dt": "2023-01-15",
        "metric_value": 123.45,
    }

    @staticmethod
    def _setup_api_time_series(
        period: str,
        theme: str,
        sub_theme: str,
        topic: str,
        geography_type: str,
        geography: str,
        metric: str,
        stratum: str,
        sex: str,
        year: int,
        epiweek: int,
        dt: str,
        metric_value: float,
    ) -> APITimeSeries:
        return APITimeSeries.objects.create(
            period=period,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            geography_type=geography_type,
            geography=geography,
            metric=metric,
            stratum=stratum,
            sex=sex,
            year=year,
            epiweek=epiweek,
            dt=dt,
            metric_value=metric_value,
        )

    @pytest.mark.parametrize("path", ["/downloads/v2", "/api/downloads/v2"])
    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload to request a download
        And an authenticated APIClient
        When the `POST /downloads/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        path_without_trailing_forward_slash: str = path
        self._setup_api_time_series(**self.api_timeseries_data)
        valid_payload = {
            "file_format": "json",
            "plots": [
                {
                    "metric": self.metric,
                    "stratum": self.stratum,
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=path_without_trailing_forward_slash,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("path", ["/downloads/v2/", "/api/downloads/v2/"])
    @pytest.mark.django_db
    def test_json_download_returns_correct_response(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload to request a download
        And an authenticated APIClient
        When the `POST /downloads/v2/` endpoint is hit
        Then the response contains the expected output in json format
        """
        # Given
        self._setup_api_time_series(**self.api_timeseries_data)
        valid_payload = {
            "file_format": "json",
            "plots": [
                {
                    "metric": self.metric,
                    "stratum": self.stratum,
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert response.headers["Content-Type"] == "application/coreapi+json"

        # Check the format of the output is as expected
        assert type(response.data[0]) == OrderedDict

        # Check the output itself is as expected
        assert response.data[0] == self.api_timeseries_data

    @pytest.mark.parametrize("path", ["/downloads/v2/", "/api/downloads/v2/"])
    @pytest.mark.django_db
    def test_csv_download_returns_correct_response(
        self, path: str, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload to request a download
        And an authenticated APIClient
        When the `POST /downloads/v2/` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        self._setup_api_time_series(**self.api_timeseries_data)
        valid_payload = {
            "file_format": "csv",
            "plots": [
                {
                    "metric": self.metric,
                    "stratum": self.stratum,
                }
            ],
        }

        expected_csv_heading = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "stratum",
            "sex",
            "year",
            "dt",
            "metric_value",
        ]
        expected_csv_content = [
            [
                "infectious_disease",
                "respiratory",
                "COVID-19",
                "Nation",
                "England",
                "new_deaths_7day_avg",
                "default",
                "M",
                "2023",
                "2023-01-15",
                "123.45",
            ]
        ]

        # When
        response: Response = authenticated_api_client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate csv is being returned
        assert response.headers["Content-Type"] == "text/csv"

        # Check the output itself is as expected
        csv_file = csv.reader(io.StringIO(response.content.decode("utf-8")))
        csv_output = list(csv_file)
        csv_header = csv_output.pop(0)

        assert csv_header == expected_csv_heading
        assert csv_output == expected_csv_content

    @pytest.mark.parametrize("path", ["/downloads/v2/", "/api/downloads/v2/"])
    @pytest.mark.django_db
    def test_post_request_without_api_key_is_unauthorized(self, path: str):
        """
        Given an APIClient which is not authenticated
        When the `GET /downloads/v2/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.post(path=path, data={})

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED
