import copy
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.tables.subplot_tables.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestTablesSubplotView:
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
        return "/api/tables/subplot/v1/"

    @pytest.mark.django_db
    def test_returns_correct_data(self):
        """
        Given a valid payload to create a subplot table
        When a POST request is made to `/api/tables/subplot/v1/`
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
        # The response is returned as groups dictated by the `x_axis`
        # which in this case is `geography`
        expected_response_data = [
            {
                "reference": "England",
                "values": [
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (12 months)",
                        "value": "88.0000",
                    },
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (24 months)",
                        "value": "78.0000",
                    },
                    # Since there is no England / MMR1 / 24m record then
                    # nothing is returned in its place
                ],
            },
            {
                "reference": "North East",
                "values": [
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (12 months)",
                        "value": "97.0000",
                    },
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (24 months)",
                        "value": "89.0000",
                    },
                    {
                        "in_reporting_delay_period": False,
                        "label": "MMR1 (24 months)",
                        "value": "84.0000",
                    },
                ],
            },
            {
                "reference": "Darlington",
                "values": [
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (12 months)",
                        "value": "90.0000",
                    },
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (24 months)",
                        "value": "87.0000",
                    },
                    {
                        "in_reporting_delay_period": False,
                        "label": "MMR1 (24 months)",
                        "value": "93.0000",
                    },
                ],
            },
        ]

        assert response.data == expected_response_data

    @pytest.mark.django_db
    def test_returns_correct_data_for_filtered_metric_value_ranges(self):
        """
        Given a valid payload to create a subplot table
            with restricted permissible `metric_value_ranges`
        When a POST request is made to `/api/tables/subplot/v1/`
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
        # The response is returned as groups dictated by the `x_axis`
        # which in this case is `geography`
        expected_response_data = [
            # Since all the `England` record were under the `metric_value` of 90
            # then they `England` gets excluded entirely
            {
                "reference": "North East",
                "values": [
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (12 months)",
                        "value": "97.0000",
                    },
                    # The North East only had the 1 record with a high enough `metric_value
                ],
            },
            {
                "reference": "Darlington",
                "values": [
                    {
                        "in_reporting_delay_period": False,
                        "label": "6-in-1 (12 months)",
                        "value": "90.0000",
                    },
                    # Darlington will be given back excluding 1 of its records
                    # since that fell outside the permissible `metric_value_ranges`
                    {
                        "in_reporting_delay_period": False,
                        "label": "MMR1 (24 months)",
                        "value": "93.0000",
                    },
                ],
            },
        ]

        assert response.data == expected_response_data

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(self):
        """
        Given a valid payload to create a table
        When the `POST /api/tables/subplot/v1` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        valid_payload = REQUEST_PAYLOAD_EXAMPLE
        path = "/api/tables/subplot/v1"
        self._create_example_core_timeseries()

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_returns_400_when_data_not_available(self):
        """
        Given a valid payload to create a table
            but no data available for that payload
        When a POST request is made to `/api/tables/subplot/v1/`
        Then the response is an HTTP 400 BAD REQUEST
        """
        # Given
        client = APIClient()
        valid_payload = REQUEST_PAYLOAD_EXAMPLE

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST != HTTPStatus.OK
