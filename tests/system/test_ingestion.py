import json
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from ingestion.file_ingestion import file_ingester
from metrics.data.models.core_models import CoreTimeSeries


class TestIngestion:
    @pytest.mark.django_db
    def test_data_can_be_ingested_and_queried_from_tables_endpoint(
        self, example_timeseries_data: list[dict[str, str | float]]
    ):
        """
        Given some sample timeseries data
        When the data is uploaded via the `file_ingester()`
        Then a subsequent request made to the `tables` endpoint
            returns the correct data
        """
        # Given
        fake_data = mock.Mock()
        fake_data.readlines.return_value = [json.dumps(example_timeseries_data)]
        fake_data.name = "metric_COVID-19_deaths_ONSByDay"
        api_client = APIClient()

        assert CoreTimeSeries.objects.count() == 0

        # When
        file_ingester(file=fake_data)

        # Then
        assert CoreTimeSeries.objects.count() == 2

        path = "/api/tables/v4/"
        timeseries_data: dict[str, str | float] = example_timeseries_data[0]
        valid_tables_endpoint_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": timeseries_data["topic"],
                    "metric": timeseries_data["metric"],
                    "date_from": "2020-01-01",
                    "chart_type": "waffle",
                }
            ],
        }

        response: Response = api_client.post(
            path=path, data=valid_tables_endpoint_payload, format="json"
        )
        response_data = response.data
        assert float(response_data[0]["values"][0]["value"]) == float(
            timeseries_data["metric_value"]
        )
