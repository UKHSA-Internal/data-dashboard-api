import copy
import csv
import io

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.downloads.subplot_downloads.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from tests.integration.metrics.api.views.downloads.subplot_downloads.common import (
    create_example_core_timeseries,
)


class TestDownloadsSubplotView:
    @property
    def path(self) -> str:
        return "/api/downloads/subplot/v1/"

    @pytest.mark.django_db
    def test_returns_correct_data_for_csv_download(self):
        """
        Given a valid payload to create a JSON subplot download
        When a POST request is made to `/api/downloads/subplot/v1/`
        Then the correct data is returned in the response
        """
        # Given
        client = APIClient()
        valid_payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
        valid_payload["file_format"] = "csv"
        create_example_core_timeseries()

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        csv_reader = csv.DictReader(io.StringIO(response.text))
        rows = list(csv_reader)

        expected_rows = [
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "6-in-1",
                "geography_type": "Nation",
                "geography": "England",
                "metric": "6-in-1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "12m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "88.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "6-in-1",
                "geography_type": "Nation",
                "geography": "England",
                "metric": "6-in-1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "24m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "78.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "",
                "sub_theme": "",
                "topic": "",
                "geography_type": "",
                "geography": "",
                "metric": "",
                "sex": "",
                "age": "",
                "stratum": "",
                "year": "",
                "date": "",
                "metric_value": "",
                "in_reporting_delay_period": "",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "6-in-1",
                "geography_type": "Region",
                "geography": "North East",
                "metric": "6-in-1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "12m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "97.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "6-in-1",
                "geography_type": "Region",
                "geography": "North East",
                "metric": "6-in-1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "24m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "89.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "MMR1",
                "geography_type": "Region",
                "geography": "North East",
                "metric": "MMR1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "24m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "84.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "",
                "sub_theme": "",
                "topic": "",
                "geography_type": "",
                "geography": "",
                "metric": "",
                "sex": "",
                "age": "",
                "stratum": "",
                "year": "",
                "date": "",
                "metric_value": "",
                "in_reporting_delay_period": "",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "6-in-1",
                "geography_type": "Upper Tier Local Authority",
                "geography": "Darlington",
                "metric": "6-in-1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "12m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "90.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "6-in-1",
                "geography_type": "Upper Tier Local Authority",
                "geography": "Darlington",
                "metric": "6-in-1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "24m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "87.0000",
                "in_reporting_delay_period": "False",
            },
            {
                "theme": "immunisation",
                "sub_theme": "childhood-vaccines",
                "topic": "MMR1",
                "geography_type": "Upper Tier Local Authority",
                "geography": "Darlington",
                "metric": "MMR1_coverage_coverageByYear",
                "sex": "all",
                "age": "all",
                "stratum": "24m",
                "year": "2023",
                "date": "2021-03-31",
                "metric_value": "93.0000",
                "in_reporting_delay_period": "False",
            },
        ]

        assert len(rows) == len(expected_rows)
