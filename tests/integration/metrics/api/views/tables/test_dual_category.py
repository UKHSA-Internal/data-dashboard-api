import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, CoreHeadline
from tests.factories.metrics.headline import CoreHeadlineFactory


@pytest.mark.django_db
class TestDualCategoryTablesView:
    @property
    def path(self) -> str:
        return "/api/tables/dual-category/v1/"

    def test_timeseries_plot(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid dual-category timeseries payload
        When the dual-category tables endpoint is called
        Then the response groups values by date with segment labels
        """

        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        latest_timeseries: CoreTimeSeries = core_timeseries_example[-1]
        topic: str = core_timeseries.metric.metric_group.topic.name
        metric: str = core_timeseries.metric.name

        valid_payload = {
            "x_axis": "date",
            "y_axis": "metric",
            "static_fields": {
                "date_from": "2000-01-01",
                "date_to": datetime.date.today(),
                "metric": metric,
                "topic": topic,
            },
            "secondary_category": "age",
            "segments": [
                {
                    "secondary_field_value": "all",
                    "label": "All ages",
                },
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.data[0]["reference"] == latest_timeseries.date.isoformat()
        assert response.data[0]["values"] == [
            {
                "label": "All ages",
                "value": "123.0000",
                "in_reporting_delay_period": False,
            }
        ]

    def test_headline_plot(
        self,
        core_headline_example: CoreHeadline,
    ):
        """
        Given a valid dual-category headline payload
        When the dual-category tables endpoint is called
        Then the response groups values by primary axis with segment labels
        """
        # Given
        client = APIClient()
        topic: str = core_headline_example.metric.metric_group.topic.name
        metric: str = core_headline_example.metric.name

        CoreHeadlineFactory.create_record(
            metric_value=123.0000,
            metric=metric,
            topic=topic,
            geography="England",
            geography_type="Nation",
            geography_code="E92000001",
            age="default",
            stratum="default",
            sex="m",
            refresh_date=core_headline_example.refresh_date,
            period_start=core_headline_example.period_start,
            period_end=core_headline_example.period_end,
        )

        valid_payload = {
            "x_axis": "age",
            "y_axis": "metric",
            "primary_field_values": [
                "default",
            ],
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

        expected_response = [
            {
                "reference": "default",
                "values": [
                    {
                        "label": "0 to 4 years female",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "0 to 4 years male",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            }
        ]

        # Then
        assert response.status_code == HTTPStatus.OK
        assert expected_response == response.data
