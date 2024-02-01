import csv
import datetime
import io
from collections import OrderedDict
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, Geography
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestDownloadsView:
    core_timeseries_data = {
        "metric_frequency": "D",
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "Nation",
        "geography": "England",
        "metric": "COVID-19_cases_rateRollingMean",
        "stratum": "default",
        "sex": "f",
        "age": "all",
        "year": 2023,
        "epiweek": 1,
        "date": "2023-01-15",
        "metric_value": 123.45,
    }

    def _build_valid_payload(self) -> dict[str, str | list[dict[str, str]]]:
        return {
            "file_format": "csv",
            "plots": [
                {
                    "metric": self.core_timeseries_data["metric"],
                    "topic": self.core_timeseries_data["topic"],
                    "stratum": self.core_timeseries_data["stratum"],
                    "age": self.core_timeseries_data["age"],
                    "sex": self.core_timeseries_data["sex"],
                    "geography": self.core_timeseries_data["geography"],
                    "geography_type": self.core_timeseries_data["geography_type"],
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }

    def _create_example_core_time_series(self) -> CoreTimeSeries:
        return CoreTimeSeriesFactory.create_record(
            metric_value=self.core_timeseries_data["metric_value"],
            theme_name=self.core_timeseries_data["theme"],
            sub_theme_name=self.core_timeseries_data["sub_theme"],
            topic_name=self.core_timeseries_data["topic"],
            metric_name=self.core_timeseries_data["metric"],
            geography_name=self.core_timeseries_data["geography"],
            geography_type_name=self.core_timeseries_data["geography_type"],
            stratum_name=self.core_timeseries_data["stratum"],
            age_name=self.core_timeseries_data["age"],
            sex=self.core_timeseries_data["sex"],
            year=self.core_timeseries_data["year"],
            epiweek=self.core_timeseries_data["epiweek"],
            date=self.core_timeseries_data["date"],
        )

    @property
    def path(self) -> str:
        return "/api/downloads/v2/"

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        self._create_example_core_time_series()
        valid_payload = self._build_valid_payload()
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
        core_time_series = self._create_example_core_time_series()
        valid_payload = self._build_valid_payload()
        valid_payload["file_format"] = "json"

        # When
        response: Response = client.post(
            path=self.path,
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
        returned_obj = response.data[0]
        expected_data = OrderedDict(
            [
                ("theme", core_time_series.metric.topic.sub_theme.theme.name),
                ("sub_theme", core_time_series.metric.topic.sub_theme.name),
                ("topic", core_time_series.metric.topic.name),
                ("geography_type", core_time_series.geography.geography_type.name),
                ("geography", core_time_series.geography.name),
                ("metric", core_time_series.metric.name),
                ("age", core_time_series.age.name),
                ("stratum", core_time_series.stratum.name),
                ("sex", core_time_series.sex),
                ("year", core_time_series.year),
                ("date", core_time_series.date),
                ("metric_value", f"{core_time_series.metric_value:.4f}"),
            ]
        )
        assert returned_obj == expected_data

    @pytest.mark.django_db
    def test_csv_download_returns_correct_response(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        client = APIClient()
        core_time_series = self._create_example_core_time_series()
        valid_payload = self._build_valid_payload()

        # When
        response: Response = client.post(
            path=self.path,
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
        csv_headers = csv_output.pop(0)

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
        assert csv_headers == expected_csv_headings

        expected_csv_content = [
            [
                core_time_series.metric.topic.sub_theme.theme.name,
                core_time_series.metric.topic.sub_theme.name,
                core_time_series.metric.topic.name,
                core_time_series.geography.geography_type.name,
                core_time_series.geography.name,
                core_time_series.metric.name,
                core_time_series.sex,
                core_time_series.age.name,
                core_time_series.stratum.name,
                str(core_time_series.year),
                core_time_series.date,
                f"{core_time_series.metric_value:.4f}",
            ]
        ]
        assert csv_output == expected_csv_content

    @pytest.mark.django_db
    def test_returns_bad_request_response_for_invalid_data(self):
        """
        Given a payload to request a download for non-existent data
        When the `POST /api/downloads/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload()
        valid_payload["plots"][0]["date_from"] = "2000-01-01"
        valid_payload["plots"][0]["date_to"] = "2000-12-31"

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.django_db
    def test_returns_bad_request_response_for_sql_injection_input(self):
        """
        Given a payload containing a SQL injection attack
        When the `POST /api/downloads/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        And the underlying SQL query is escaped and rendered harmless
        """
        # Given
        client = APIClient()
        self._create_example_core_time_series()

        attack_payload = self._build_valid_payload()
        table_name: str = Geography.objects.model._meta.db_table
        sql_injection_attack_value = f"'; DELETE FROM {table_name}"
        attack_payload["plots"][0]["geography"] = sql_injection_attack_value

        # When
        response: Response = client.post(
            path=self.path,
            data=attack_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert Geography.objects.exists()
