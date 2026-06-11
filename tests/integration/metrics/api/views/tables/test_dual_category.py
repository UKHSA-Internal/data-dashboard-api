import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, CoreHeadline


@pytest.mark.django_db
class TestTablesView:
    @property
    def path(self) -> str:
        return "/api/tables/dual-category/v1/"

    def test_timeseries_plot(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/v4/` endpoint is hit with a single plot
        Then the response is of the correct format
        """
        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic: str = core_timeseries.metric.metric_group.topic.name
        metric: str = core_timeseries.metric.name

        valid_payload = {
            "x_axis": "age",
            "label": "Dual category by age / sex",
            "x_axis_title": "",
            "primary_field_values": [
                "00-04",
            ],
            "y_axis": "metric",
            "y_axis_title": "",
            "static_fields": {
                "date_from": "2000-01-01",
                "date_to": datetime.date.today(),
                "metric": metric,
                "topic": topic,
            },
            "secondary_category": "sex",
            "segments": [
                {
                    "secondary_field_value": "f",
                    "label": "0 to 4 years female",
                },
                {
                    "secondary_field_value": "m",
                    "label": "0 to 4 years male",
                },
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        expected_response = [
            {
                "reference": "all",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            }
        ]

        assert expected_response == response.data

    def test_headline_plot(
        self,
        core_headline_example: CoreHeadline,
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/v4/` endpoint is hit with a single plot
        Then the response is of the correct format
        """
        # Given
        client = APIClient()
        topic: str = core_headline_example.metric.metric_group.topic.name
        metric: str = core_headline_example.metric.name

        valid_payload = {
            "x_axis": "age",
            "label": "Dual category by age / sex",
            "x_axis_title": "",
            "primary_field_values": [
                "00-04",
            ],
            "y_axis": "metric",
            "y_axis_title": "",
            "static_fields": {
                "date_from": "2000-01-01",
                "date_to": datetime.date.today(),
                "metric": metric,
                "topic": topic,
            },
            "secondary_category": "sex",
            "segments": [
                {
                    "secondary_field_value": "f",
                    "label": "0 to 4 years female",
                },
                {
                    "secondary_field_value": "m",
                    "label": "0 to 4 years male",
                },
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        expected_response = [
            {
                "reference": "default",
                "values": [
                    {
                        "label": "Amount",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Amount",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            }
        ]

        assert expected_response == response.data
