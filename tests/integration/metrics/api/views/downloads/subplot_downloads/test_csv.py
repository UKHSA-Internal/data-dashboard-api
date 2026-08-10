import copy
import csv
import io
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.views.downloads.subplot_downloads.request_example import (
    REQUEST_PAYLOAD_EXAMPLE,
)
from tests.factories.common.auth.permissions import UserPermissionsFactory
from tests.integration.metrics.api.views.downloads.subplot_downloads.common import (
    create_example_core_timeseries,
    create_example_core_headlines,
)


class TestDownloadsSubplotView:
    @property
    def path(self) -> str:
        return "/api/downloads/subplot/v1/"

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("authenticated_user", "no_of_expected_rows"),
        [
            (True, 5),
            (False, 3),
        ],
    )
    def test_csv_download_for_timeseries_data_with_filtered_metric_value_ranges(
        self, authenticated_user, no_of_expected_rows
    ):
        """
        Given a valid payload to create a JSON subplot download
            which filters for a particular `metric_value_range`
        When a POST request is made to `/api/downloads/subplot/v1/`
        Then the correct data is returned in the response
        """
        # Given
        client = APIClient()
        if authenticated_user:
            mock_user = mock.MagicMock()
            mock_user.username = "restricted-user"

            mock_user.permission_sets = UserPermissionsFactory(
                [],
                has_global_access=True,
            )
            client.force_authenticate(user=mock_user, token="token")

        valid_payload = copy.deepcopy(REQUEST_PAYLOAD_EXAMPLE)
        valid_payload["file_format"] = "csv"
        valid_payload["chart_parameters"]["metric_value_ranges"] = [
            # We're asking for 1 boundary, excluding anything under 90
            {"start": 90, "end": 100}
        ]
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
                        "label": "North West",
                        "geography": "North West",
                        "geography_type": "Region",
                        "line_colour": "COLOUR_4_ORANGE",
                    },
                    {
                        "label": "Leeds",
                        "geography": "Leeds",
                        "geography_type": "Upper Tier Local Authority",
                        "line_colour": "COLOUR_5_DARK_GREY",
                    },
                ],
            }
        )

        create_example_core_timeseries()

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        csv_reader = csv.DictReader(io.StringIO(response.text))
        rows = list(csv_reader)

        assert len(rows) == no_of_expected_rows

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ("authenticated_user", "no_of_expected_rows"),
        [
            (True, 4),
            (False, 3),
        ],
    )
    def test_csv_download_for_headline_data(
        self, authenticated_user, no_of_expected_rows
    ):
        """
        Given a valid payload to create a JSON subplot download
        When a POST request is made to `/api/downloads/subplot/v1/`
        Then the correct data is returned in the response
        """
        # Given
        client = APIClient()
        if authenticated_user:
            mock_user = mock.MagicMock()
            mock_user.username = "restricted-user"

            mock_user.permission_sets = UserPermissionsFactory(
                [],
                has_global_access=True,
            )
            client.force_authenticate(user=mock_user, token="token")

        valid_payload = {
            "file_format": "csv",
            "chart_height": 300,
            "chart_width": 900,
            "chart_parameters": {
                "x_axis": "geography",
                "y_axis": "metric",
                "theme": "infectious_disease",
                "sub_theme": "respiratory",
                "date_from": "2021-01-31",
                "date_to": "2021-12-31",
                "age": "all",
                "sex": "all",
                "stratum": "default",
                "metric_value_ranges": [
                    {"start": 0, "end": 80},
                    {"start": 80.0001, "end": 85},
                    {"start": 85.0001, "end": 90},
                    {"start": 90.0001, "end": 95},
                    {"start": 95.0001, "end": 100},
                ],
            },
            "subplots": [
                {
                    "subplot_title": "COVID-19 tests",
                    "subplot_parameters": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_headline_tests_7DayTotal",
                        "stratum": "default",
                    },
                    "plots": [
                        {
                            "label": "England",
                            "geography": "England",
                            "geography_type": "Nation",
                            "line_colour": "COLOUR_1_DARK_BLUE",
                        },
                        {
                            "label": "North East",
                            "geography": "North East",
                            "geography_type": "Region",
                            "line_colour": "COLOUR_2_TURQUOISE",
                        },
                        {
                            "label": "Darlington",
                            "geography": "Darlington",
                            "geography_type": "Upper Tier Local Authority",
                            "line_colour": "COLOUR_3_DARK_PINK",
                        },
                        {
                            "label": "Scotland",
                            "geography": "Scotland",
                            "geography_type": "Nation",
                            "line_colour": "COLOUR_4_ORANGE",
                        },
                    ],
                },
            ],
        }
        create_example_core_headlines()

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        csv_reader = csv.DictReader(io.StringIO(response.text))
        rows = list(csv_reader)

        assert len(rows) == no_of_expected_rows
