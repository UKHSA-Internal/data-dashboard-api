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
    api_timeseries_record = {
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

    @property
    def path(self) -> str:
        return "/downloads/v2/"

    @pytest.mark.django_db
    def test_json_download_returns_correct_response(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload to request a download
        And an authenticated APIClient
        When the `POST /downloads/v2/json` endpoint is hit
        Then the response contains the expected output
        """
        # Given
        self._setup_api_time_series(**self.api_timeseries_record)
        valid_payload = {
            "format": "json",
            "plots": [
                {
                    "metric": self.metric,
                    "stratum": self.stratum,
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert response.headers["Content-Type"] == "application/coreapi+json"

        # Check the format of the output is as expected
        assert type(response.data[0]) == OrderedDict

        # Check the output itself is as expected
        assert response.data[0] == self.api_timeseries_record

    @pytest.mark.django_db
    def test_csv_download_returns_correct_response(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a valid payload to request a download
        And an authenticated APIClient
        When the `POST /downloads/v2/csv` endpoint is hit
        Then the response contains the expected output
        """
        # Given
        self._setup_api_time_series(**self.api_timeseries_record)
        valid_payload = {
            "format": "csv",
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
                "2023-01-15",
                "123.45",
            ]
        ]

        # When
        response: Response = authenticated_api_client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert response.headers["Content-Type"] == "text/csv"

        # Check the output itself is as expected
        csv_file = csv.reader(io.StringIO(response.content.decode("utf-8")))
        csv_output = list(csv_file)
        csv_header = csv_output.pop(0)

        assert csv_header == expected_csv_heading
        assert csv_output == expected_csv_content
