import copy
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.downloads.subplot_downloads.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestDownloadsSubplotView:
    @classmethod
    def _create_example_core_timeseries(cls) -> None:
        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="6-in-1",
            metric_name=f"6-in-1_coverage_coverageByYear",
            stratum_name="12m",
            date="2021-03-31",
            geography_name="Darlington",
            geography_type_name="Upper Tier Local Authority",
            metric_value=90,
        )
        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="6-in-1",
            metric_name=f"6-in-1_coverage_coverageByYear",
            stratum_name="12m",
            date="2021-03-31",
            geography_name="North East",
            geography_type_name="Region",
            metric_value=97,
        )
        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="6-in-1",
            metric_name=f"6-in-1_coverage_coverageByYear",
            stratum_name="12m",
            date="2021-03-31",
            geography_name="England",
            geography_type_name="Nation",
            metric_value=88,
        )

        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="6-in-1",
            metric_name=f"6-in-1_coverage_coverageByYear",
            stratum_name="24m",
            date="2021-03-31",
            geography_name="Darlington",
            geography_type_name="Upper Tier Local Authority",
            metric_value=87,
        )
        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="6-in-1",
            metric_name=f"6-in-1_coverage_coverageByYear",
            stratum_name="24m",
            date="2021-03-31",
            geography_name="North East",
            geography_type_name="Region",
            metric_value=89,
        )
        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="6-in-1",
            metric_name=f"6-in-1_coverage_coverageByYear",
            stratum_name="24m",
            date="2021-03-31",
            geography_name="England",
            geography_type_name="Nation",
            metric_value=78,
        )

        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="MMR1",
            metric_name="MMR1_coverage_coverageByYear",
            stratum_name="24m",
            date="2021-03-31",
            geography_name="Darlington",
            geography_type_name="Upper Tier Local Authority",
            metric_value=93,
        )
        CoreTimeSeriesFactory.create_record(
            theme_name="immunisation",
            sub_theme_name="childhood-vaccines",
            topic_name="MMR1",
            metric_name="MMR1_coverage_coverageByYear",
            stratum_name="24m",
            date="2021-03-31",
            geography_name="North East",
            geography_type_name="Region",
            metric_value=84,
        )
        # There is intentionally no corresponding record for England / MMR1 / 24m

    @property
    def path(self) -> str:
        return "/api/downloads/subplot/v1/"

    @pytest.mark.django_db
    def test_returns_correct_data(self):
        """
        Given a valid payload to create a JSON subplot download
        When a POST request is made to `/api/downloads/subplot/v1/`
        Then the correct data is returned in the response
        """
        # Given
        client = APIClient()
        valid_payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
        self._create_example_core_timeseries()

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        expected_response_data = [
            # The 'England' subplot group
            [
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Nation",
                    "geography": "England",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "12m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "88.0000",
                    "in_reporting_delay_period": False,
                },
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Nation",
                    "geography": "England",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "24m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "78.0000",
                    "in_reporting_delay_period": False,
                },
            ],
            # The 'North East' subplot group
            [
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Region",
                    "geography": "North East",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "12m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "97.0000",
                    "in_reporting_delay_period": False,
                },
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Region",
                    "geography": "North East",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "24m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "89.0000",
                    "in_reporting_delay_period": False,
                },
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "MMR1",
                    "geography_type": "Region",
                    "geography": "North East",
                    "metric": "MMR1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "24m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "84.0000",
                    "in_reporting_delay_period": False,
                },
            ],
            # The 'Darlington' subplot group
            [
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Upper Tier Local Authority",
                    "geography": "Darlington",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "12m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "90.0000",
                    "in_reporting_delay_period": False,
                },
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Upper Tier Local Authority",
                    "geography": "Darlington",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "24m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "87.0000",
                    "in_reporting_delay_period": False,
                },
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "MMR1",
                    "geography_type": "Upper Tier Local Authority",
                    "geography": "Darlington",
                    "metric": "MMR1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "24m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "93.0000",
                    "in_reporting_delay_period": False,
                },
            ],
        ]

        assert response.data == expected_response_data

    @pytest.mark.django_db
    def test_returns_correct_data_for_filtered_metric_value_ranges(self):
        """
        Given a valid payload to create a JSON subplot download
            with restricted permissible `metric_value_ranges`
        When a POST request is made to `/api/downloads/subplot/v1/`
        Then the correct data is returned in the response
            conforming to the allowable `metric_value_ranges`
        """
        # Given
        client = APIClient()
        valid_payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
        valid_payload["chart_parameters"]["metric_value_ranges"] = [
            # We're asking for 1 boundary, excluding anything under 90
            {"start": 90, "end": 100}
        ]
        self._create_example_core_timeseries()

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        expected_response_data = [
            # The `England` subplot group was omitted altogether
            # as it did not contain any records within the permissible `metric_value_ranges`
            # The `North East` subplot group only returned the 1 record
            # which fell within the given `metric_value_ranges`
            [
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Region",
                    "geography": "North East",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "12m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "97.0000",
                    "in_reporting_delay_period": False,
                }
            ],
            # The Darlington subplot group with only 2 records
            # since the 3rd fell outside the `metric_value_ranges`
            [
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "6-in-1",
                    "geography_type": "Upper Tier Local Authority",
                    "geography": "Darlington",
                    "metric": "6-in-1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "12m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "90.0000",
                    "in_reporting_delay_period": False,
                },
                {
                    "theme": "immunisation",
                    "sub_theme": "childhood-vaccines",
                    "topic": "MMR1",
                    "geography_type": "Upper Tier Local Authority",
                    "geography": "Darlington",
                    "metric": "MMR1_coverage_coverageByYear",
                    "age": "all",
                    "stratum": "24m",
                    "sex": "all",
                    "year": 2023,
                    "date": "2021-03-31",
                    "metric_value": "93.0000",
                    "in_reporting_delay_period": False,
                },
            ],
        ]
        assert response.data == expected_response_data

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(self):
        """
        Given a valid payload to create a table
        When the `POST /api/downloads/subplot/v1` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        valid_payload = REQUEST_PAYLOAD_EXAMPLE
        path = "/api/downloads/subplot/v1"
        self._create_example_core_timeseries()

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK
