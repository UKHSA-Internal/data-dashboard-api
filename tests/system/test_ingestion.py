import datetime
import json
from collections import OrderedDict
from decimal import Decimal
from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from ingestion.file_ingestion import file_ingester
from metrics.data.models.core_models import CoreTimeSeries

FAKE_FILE_NAME = "COVID-19_deaths_ONSByDay.json"


def _create_fake_file(data: list[dict[str, str | float]], file_name: str) -> mock.Mock:
    fake_file = mock.Mock()
    fake_file.readlines.return_value = [json.dumps(data)]
    fake_file.name = file_name
    return fake_file


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
        fake_data = _create_fake_file(
            data=example_timeseries_data, file_name=FAKE_FILE_NAME
        )

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

    @pytest.mark.django_db
    def test_when_multiple_files_are_ingested_the_correct_data_is_queried_for(
        self, example_timeseries_data: list[dict[str, str | float]]
    ):
        """
        Given multiple ingested files of
            new data, no new functional data, and retrospective updates
        When the data is queried for via the model manager
        Then the correct data is returned at each point in time
        """
        # Given
        file_name = FAKE_FILE_NAME
        first_sample_data = example_timeseries_data
        query_payload = {
            "x_axis": "date",
            "y_axis": "metric_value",
            "topic_name": first_sample_data[0]["topic"],
            "metric_name": first_sample_data[0]["metric"],
            "date_from": "2020-01-01",
            "date_to": "2023-10-31",
        }
        first_data_file = _create_fake_file(data=first_sample_data, file_name=file_name)

        second_refresh_date = datetime.date(year=2023, month=10, day=30)
        second_data_file_with_no_functional_updates = (
            self._rebuild_file_with_updated_refresh_date_only(
                data=example_timeseries_data,
                refresh_date=second_refresh_date,
                file_name=file_name,
            )
        )

        final_refresh_date = datetime.date(year=2023, month=10, day=31)
        updated_metric_value = 99.0000
        third_data_file_with_retrospective_updates = (
            self._rebuild_file_with_single_retrospective_update(
                data=example_timeseries_data,
                refresh_date=final_refresh_date,
                metric_value=updated_metric_value,
                file_name=file_name,
            )
        )

        date_format = "%Y-%m-%d"
        first_date: datetime.date = datetime.datetime.strptime(
            example_timeseries_data[0]["date"], date_format
        ).date()
        second_date: datetime.date = datetime.datetime.strptime(
            example_timeseries_data[1]["date"], date_format
        ).date()

        # When / Then
        # Check that the 1st file is ingested properly
        file_ingester(file=first_data_file)
        filtered_core_time_series = CoreTimeSeries.objects.filter_for_x_and_y_values(
            **query_payload
        )
        assert filtered_core_time_series.count() == 2
        assert (first_date, Decimal("0.0000")) in filtered_core_time_series
        assert (second_date, Decimal("0.0000")) in filtered_core_time_series

        # Check that the 2nd file is ingested
        file_ingester(file=second_data_file_with_no_functional_updates)
        filtered_core_time_series = CoreTimeSeries.objects.filter_for_x_and_y_values(
            **query_payload
        )
        assert filtered_core_time_series.count() == 2
        # The `refresh_date` remains as per the original file
        assert second_refresh_date not in filtered_core_time_series.values_list(
            "refresh_date", flat=True
        )
        # And the returned data remains functionally the same
        assert (first_date, Decimal("0.0000")) in filtered_core_time_series
        assert (second_date, Decimal("0.0000")) in filtered_core_time_series

        # Check that the 3rd file is ingested
        file_ingester(file=third_data_file_with_retrospective_updates)
        filtered_core_time_series = CoreTimeSeries.objects.filter_for_x_and_y_values(
            **query_payload
        )
        assert filtered_core_time_series.count() == 2
        returned_refresh_dates = filtered_core_time_series.values_list(
            "refresh_date", flat=True
        )
        assert second_refresh_date not in returned_refresh_dates
        # The new `refresh_date` for the 1 retrospective update is included
        assert final_refresh_date in returned_refresh_dates

        # And the returned data contains the retrospective update
        # as well as the other original data point
        assert (first_date, Decimal(updated_metric_value)) in filtered_core_time_series
        assert (second_date, Decimal("0.0000")) in filtered_core_time_series

    @pytest.mark.django_db
    def test_data_is_deduplicated_on_write_to_db_and_return_latest_data_from_apis(
        self, example_timeseries_data: list[dict[str, str | float]]
    ):
        """
        Given some sample timeseries data
        And another copy of that same sample with new `refresh_date` stamps
        And then a new version of the sample containing retrospective updates
        When all the files are uploaded via the `file_ingester()`
        Then the APIs should return the latest-functional data
        """
        # Given
        file_name = FAKE_FILE_NAME
        first_sample_data = example_timeseries_data
        first_data_file = _create_fake_file(data=first_sample_data, file_name=file_name)

        second_refresh_date = datetime.date(year=2023, month=10, day=30)
        second_data_file_with_no_functional_updates = (
            self._rebuild_file_with_updated_refresh_date_only(
                data=example_timeseries_data,
                refresh_date=second_refresh_date,
                file_name=file_name,
            )
        )

        final_refresh_date = datetime.date(year=2023, month=10, day=31)
        updated_metric_value = 99.0000
        third_data_file_with_retrospective_updates = (
            self._rebuild_file_with_single_retrospective_update(
                data=example_timeseries_data,
                refresh_date=final_refresh_date,
                metric_value=updated_metric_value,
                file_name=file_name,
            )
        )

        # When / Then
        # The 1st file is ingested we expect all the data points to be made available
        file_ingester(file=first_data_file)
        assert CoreTimeSeries.objects.all().count() == 2

        # Check that the `tables/` endpoint returns the correct data
        # which matches the first ingested file
        topic = example_timeseries_data[0]["topic"]
        metric = example_timeseries_data[0]["metric"]
        tables_response = self._hit_tables_endpoint(topic=topic, metric=metric)
        for row in tables_response:
            assert row["values"][0]["value"] == "0.0000"

        # Check that the public API returns the correct data
        public_api_data = self._hit_public_api(data=example_timeseries_data[0])
        assert public_api_data["count"] == 2
        assert public_api_data["results"][0]["metric"] == metric
        assert public_api_data["results"][0]["topic"] == topic
        assert str(public_api_data["results"][0]["metric_value"]) == str(0.0)

        # The 2nd file is ingested we don't expect any changes
        # because it contains no functional updates
        file_ingester(file=second_data_file_with_no_functional_updates)
        assert CoreTimeSeries.objects.all().count() == 2
        # The `refresh_date` of this file should not be written to the database
        # since the data contained in this file is considered functionally the same as existing data
        assert second_refresh_date not in CoreTimeSeries.objects.all().values_list(
            "refresh_date", flat=True
        )
        # After the 2nd file was ingested and subsequently de-duplicated
        # the `tables/` endpoint should still return the same values as before
        tables_response = self._hit_tables_endpoint(topic=topic, metric=metric)
        for row in tables_response:
            assert row["values"][0]["value"] == "0.0000"

        # The 3rd file is ingested for which we expect 1 new record
        # whilst the other data point is de-duplicated since it contained no functional update
        file_ingester(file=third_data_file_with_retrospective_updates)
        assert CoreTimeSeries.objects.all().count() == 3
        assert final_refresh_date in CoreTimeSeries.objects.all().values_list(
            "refresh_date", flat=True
        )
        tables_response = self._hit_tables_endpoint(topic=topic, metric=metric)
        assert tables_response[0]["values"][0]["value"] == "0.0000"
        # We expect the 1st row to be as per the original data
        # But the 2nd row should be updated to the latest metric_value of 99
        # Note that the extra decimal places are cast by the database column
        assert tables_response[1]["values"][0]["value"] == f"{updated_metric_value:.4f}"

        # Check that the public API also contains the retrospective updates
        # as well as the records from the first file ingestion
        public_api_data = self._hit_public_api(data=example_timeseries_data[0])
        assert public_api_data["count"] == 3
        assert public_api_data["results"][0]["metric"] == metric
        assert public_api_data["results"][0]["topic"] == topic
        assert str(public_api_data["results"][1]["metric_value"]) == str(
            updated_metric_value
        )

    @staticmethod
    def _rebuild_file_with_updated_refresh_date_only(
        data: list[dict],
        refresh_date: datetime.date,
        file_name: str,
    ) -> mock.Mock:
        sample_data_with_no_functional_updates = data
        for data_point in sample_data_with_no_functional_updates:
            data_point["refresh_date"] = str(refresh_date)
        return _create_fake_file(
            data=sample_data_with_no_functional_updates, file_name=file_name
        )

    @staticmethod
    def _rebuild_file_with_single_retrospective_update(
        data: list[dict],
        refresh_date: datetime.date,
        metric_value: float,
        file_name: str,
    ) -> mock.Mock:
        sample_data_with_one_retrospective_update = data
        for data_point in data:
            data_point["refresh_date"] = str(refresh_date)
        sample_data_with_one_retrospective_update[0]["metric_value"] = metric_value
        return _create_fake_file(
            data=sample_data_with_one_retrospective_update, file_name=file_name
        )

    @staticmethod
    def _hit_tables_endpoint(topic: str, metric: str) -> list[dict]:
        client = APIClient()

        path = "/api/tables/v4/"
        valid_tables_endpoint_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic,
                    "metric": metric,
                    "date_from": "2020-01-01",
                    "chart_type": "bar",
                }
            ],
        }

        # This forces a cache miss and ensures the latest values are recalculated
        headers = {"Cache-Force-Refresh": True}

        response: Response = client.post(
            path=path,
            data=valid_tables_endpoint_payload,
            headers=headers,
            format="json",
        )
        return response.data

    @staticmethod
    def _hit_public_api(data: dict) -> OrderedDict:
        client = APIClient()

        theme_name: str = data["parent_theme"]
        sub_theme_name: str = data["child_theme"]
        topic_name: str = data["topic"]
        geography_type_name: str = data["geography_type"]
        geography_name: str = data["geography"]
        metric_name: str = data["metric"]
        path: str = (
            f"/api/public/timeseries/"
            f"themes/{theme_name}/"
            f"sub_themes/{sub_theme_name}/"
            f"topics/{topic_name}/"
            f"geography_types/{geography_type_name}/"
            f"geographies/{geography_name}/"
            f"metrics/{metric_name}"
        )

        response: Response = client.get(path=path, format="json")
        return response.data
