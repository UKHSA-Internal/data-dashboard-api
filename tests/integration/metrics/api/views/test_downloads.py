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
        "metric_frequency": "D",
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "Nation",
        "geography": "England",
        "metric": metric,
        "stratum": stratum,
        "sex": "M",
        "age": "all",
        "year": 2023,
        "epiweek": 1,
        "date": "2023-01-15",
        "metric_value": 123.45,
    }

    @staticmethod
    def _setup_api_time_series(
        metric_frequency: str,
        theme: str,
        sub_theme: str,
        topic: str,
        geography_type: str,
        geography: str,
        metric: str,
        sex: str,
        age: str,
        stratum: str,
        year: int,
        epiweek: int,
        date: str,
        metric_value: float,
    ) -> APITimeSeries:
        return APITimeSeries.objects.create(
            metric_frequency=metric_frequency,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            geography_type=geography_type,
            geography=geography,
            metric=metric,
            sex=sex,
            age=age,
            stratum=stratum,
            year=year,
            epiweek=epiweek,
            date=date,
            metric_value=metric_value,
        )

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
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
        path_without_trailing_forward_slash = "/api/downloads/v2"

        # When
        response: Response = client.post(
            path=path_without_trailing_forward_slash,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_json_download_returns_correct_response(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in json format
        """
        # Given
        client = APIClient()
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
        path = "/api/downloads/v2/"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert "json" in response.headers["Content-Type"]

        # Check the format of the output is as expected
        assert isinstance(response.data[0], OrderedDict)

        # Check the output itself is as expected
        assert response.data[0] == self.api_timeseries_data

    @pytest.mark.django_db
    def test_csv_download_returns_correct_response(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        client = APIClient()
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
        path = "/api/downloads/v2/"

        # When
        response: Response = client.post(
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

        expected_csv_headings = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "year",
            "date",
            "metric_value",
        ]
        assert csv_header == expected_csv_headings

        expected_csv_content = [
            [
                "infectious_disease",
                "respiratory",
                "COVID-19",
                "Nation",
                "England",
                "new_deaths_7day_avg",
                "M",
                "all",
                "default",
                "2023",
                "2023-01-15",
                "123.45",
            ]
        ]
        assert csv_output == expected_csv_content
