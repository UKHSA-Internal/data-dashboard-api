import copy
import datetime
from collections import OrderedDict
from decimal import Decimal

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from ingestion.file_ingestion import data_ingester
from ingestion.utils.type_hints import INCOMING_DATA_TYPE
from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries

FAKE_FILE_NAME = "COVID-19_deaths_ONSByDay.json"
DATE_FORMAT = "%Y-%m-%d"


class TestIngestion:
    @pytest.mark.django_db
    def test_data_can_be_ingested_and_queried_from_tables_endpoint(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given some sample timeseries data
        When the data is uploaded via the `data_ingester()`
        Then a subsequent request made to the `tables` endpoint
            returns the correct data
        """
        # Given
        api_client = APIClient()
        assert CoreTimeSeries.objects.count() == 0

        # When
        data_ingester(data=example_time_series_data)

        # Then
        assert CoreTimeSeries.objects.count() == 2

        path = "/api/tables/v4/"
        valid_tables_endpoint_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": example_time_series_data["topic"],
                    "metric": example_time_series_data["metric"],
                    "date_from": "2020-01-01",
                    "chart_type": "bar",
                }
            ],
        }

        response: Response = api_client.post(
            path=path, data=valid_tables_endpoint_payload, format="json"
        )
        response_data = response.data
        # We expect the data to be returned in chronological order, starting from the most recent
        assert (
            float(response_data[0]["values"][0]["value"])
            == example_time_series_data["time_series"][1]["metric_value"]
        )
        assert (
            float(response_data[1]["values"][0]["value"])
            == example_time_series_data["time_series"][0]["metric_value"]
        )

    @pytest.mark.django_db
    def test_when_multiple_files_are_ingested_the_correct_data_is_queried_for(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given multiple ingested files of
            new data, no new functional data, and retrospective updates
        When the data is queried for via the model manager
        Then the correct data is returned at each point in time
        """
        # Given
        first_sample_data = example_time_series_data.copy()
        query_payload = {
            "fields_to_export": ["date", "metric_value"],
            "topic": first_sample_data["topic"],
            "metric": first_sample_data["metric"],
            "date_from": "2020-01-01",
            "date_to": "2023-10-31",
        }
        # When / Then
        # Check that the 1st file is ingested properly
        data_ingester(data=first_sample_data)
        filtered_core_time_series = CoreTimeSeries.objects.query_for_data(
            **query_payload
        )
        first_date: datetime.date = datetime.datetime.strptime(
            example_time_series_data["time_series"][0]["date"], DATE_FORMAT
        ).date()
        second_date: datetime.date = datetime.datetime.strptime(
            example_time_series_data["time_series"][1]["date"], DATE_FORMAT
        ).date()

        assert filtered_core_time_series.count() == 2
        first_metric_value = example_time_series_data["time_series"][0]["metric_value"]
        second_metric_value = example_time_series_data["time_series"][1]["metric_value"]
        assert (
            self._parse_date_and_metric_value_as_expected_output(
                date_value=first_date, metric_value=Decimal(str(first_metric_value))
            )
            in filtered_core_time_series
        )
        assert (
            self._parse_date_and_metric_value_as_expected_output(
                date_value=second_date, metric_value=Decimal(str(second_metric_value))
            )
            in filtered_core_time_series
        )

        # When / Then
        # Check that the 2nd file is ingested
        second_refresh_date = datetime.datetime(
            year=2023, month=10, day=30, hour=0, minute=0, second=0, tzinfo=datetime.UTC
        )
        second_data_with_no_functional_updates = (
            self._rebuild_data_with_updated_refresh_date_only(
                data=example_time_series_data,
                refresh_date=second_refresh_date,
            )
        )
        data_ingester(data=second_data_with_no_functional_updates)
        filtered_core_time_series = CoreTimeSeries.objects.query_for_data(
            **query_payload
        )
        assert filtered_core_time_series.count() == 2
        # The `refresh_date` remains as per the original file
        assert second_refresh_date not in filtered_core_time_series.values_list(
            "refresh_date", flat=True
        )
        # And the returned data remains functionally the same
        assert (
            self._parse_date_and_metric_value_as_expected_output(
                date_value=first_date, metric_value=Decimal(str(first_metric_value))
            )
            in filtered_core_time_series
        )
        assert (
            self._parse_date_and_metric_value_as_expected_output(
                date_value=second_date, metric_value=Decimal(str(second_metric_value))
            )
            in filtered_core_time_series
        )

        # When / Then
        # Check that the 3rd file is ingested
        final_refresh_date = datetime.datetime(
            year=2023, month=12, day=1, hour=0, minute=0, second=0, tzinfo=datetime.UTC
        )
        updated_metric_value = 99.0000
        third_data_with_retrospective_updates = (
            self._rebuild_data_with_single_retrospective_update(
                data=example_time_series_data,
                refresh_date=final_refresh_date,
                metric_value=updated_metric_value,
            )
        )
        data_ingester(data=third_data_with_retrospective_updates)
        filtered_core_time_series = CoreTimeSeries.objects.query_for_data(
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
        assert (
            self._parse_date_and_metric_value_as_expected_output(
                date_value=first_date, metric_value=Decimal(str(updated_metric_value))
            )
            in filtered_core_time_series
        )
        assert (
            self._parse_date_and_metric_value_as_expected_output(
                date_value=second_date, metric_value=Decimal(str(second_metric_value))
            )
            in filtered_core_time_series
        )

    @classmethod
    def _parse_date_and_metric_value_as_expected_output(
        cls, date_value: datetime.date, metric_value: Decimal
    ) -> dict[str, datetime.date | Decimal]:
        return {"date": date_value, "metric_value": metric_value}

    @pytest.mark.django_db
    def test_data_is_deduplicated_on_write_to_db_and_return_latest_data_from_apis(
        self, example_time_series_data: INCOMING_DATA_TYPE
    ):
        """
        Given some sample timeseries data
        And another copy of that same sample with new `refresh_date` stamps
        And then a new version of the sample containing retrospective updates
        When all the files are uploaded via the `data_ingester()`
        Then the APIs should return the latest-functional data
        """
        # Given
        first_sample_data = example_time_series_data.copy()

        # When / Then
        # The 1st file is ingested we expect all the data points to be made available
        data_ingester(data=first_sample_data)
        assert CoreTimeSeries.objects.all().count() == 2

        # Check that the `tables/` endpoint returns the correct data
        # which matches the first ingested file
        topic = first_sample_data["topic"]
        metric = first_sample_data["metric"]
        tables_response = self._hit_tables_endpoint(topic=topic, metric=metric)
        expected_first_metric_value = (
            f"{first_sample_data['time_series'][1]['metric_value']:.4f}"
        )
        expected_second_metric_value = (
            f"{first_sample_data['time_series'][0]['metric_value']:.4f}"
        )
        returned_metric_values = [row["values"][0]["value"] for row in tables_response]
        assert returned_metric_values[0] == expected_first_metric_value
        assert returned_metric_values[1] == expected_second_metric_value

        # Check that the public API returns the correct data
        public_api_data = self._hit_public_api(data=first_sample_data)
        assert public_api_data["count"] == 2
        assert public_api_data["results"][0]["metric"] == metric
        assert public_api_data["results"][0]["topic"] == topic
        returned_metric_values = [
            f"{x['metric_value']:.4f}" for x in public_api_data["results"]
        ]
        assert expected_first_metric_value in returned_metric_values
        assert expected_second_metric_value in returned_metric_values

        # The 2nd file is ingested but we don't expect any changes
        # because it contains no functional updates
        second_refresh_date = datetime.datetime(
            year=2023, month=10, day=30, hour=0, minute=0, second=0, tzinfo=datetime.UTC
        )
        second_data_file_with_no_functional_updates = (
            self._rebuild_data_with_updated_refresh_date_only(
                data=example_time_series_data,
                refresh_date=second_refresh_date,
            )
        )
        data_ingester(data=second_data_file_with_no_functional_updates)
        assert CoreTimeSeries.objects.all().count() == 2
        # The `refresh_date` of this file should not be written to the database
        # since the data contained in this file is considered functionally the same as existing data
        assert second_refresh_date not in CoreTimeSeries.objects.all().values_list(
            "refresh_date", flat=True
        )
        # After the 2nd file was ingested and subsequently de-duplicated
        # the `tables/` endpoint should still return the same values as before
        tables_response = self._hit_tables_endpoint(topic=topic, metric=metric)
        returned_metric_values = [row["values"][0]["value"] for row in tables_response]
        assert returned_metric_values[0] == expected_first_metric_value
        assert returned_metric_values[1] == expected_second_metric_value

        # The 3rd file is ingested for which we expect 1 new record
        # whilst the other data point is de-duplicated since it contained no functional update
        final_refresh_date = datetime.datetime(
            year=2023, month=11, day=30, hour=0, minute=0, second=0, tzinfo=datetime.UTC
        )
        updated_metric_value = 99.0000
        third_data_file_with_retrospective_updates = (
            self._rebuild_data_with_single_retrospective_update(
                data=example_time_series_data,
                refresh_date=final_refresh_date,
                metric_value=updated_metric_value,
            )
        )

        data_ingester(data=third_data_file_with_retrospective_updates)
        assert CoreTimeSeries.objects.all().count() == 3
        assert final_refresh_date in CoreTimeSeries.objects.all().values_list(
            "refresh_date", flat=True
        )
        tables_response = self._hit_tables_endpoint(topic=topic, metric=metric)
        returned_metric_values = [row["values"][0]["value"] for row in tables_response]
        assert returned_metric_values[0] == expected_first_metric_value
        # We expect the 1st row to be as per the original data
        # But the 2nd row should be updated to the latest metric_value of 99
        # Note that the extra decimal places are cast by the database column
        assert returned_metric_values[1] == f"{updated_metric_value:.4f}"

        # Check that the public API contains the retrospective update
        # as well as the record from the first file ingestion
        public_api_data = self._hit_public_api(data=first_sample_data)
        assert public_api_data["count"] == 2
        assert public_api_data["results"][0]["metric"] == metric
        assert public_api_data["results"][0]["topic"] == topic
        returned_metric_values = [
            f"{x['metric_value']:.4f}" for x in public_api_data["results"]
        ]
        assert expected_first_metric_value in returned_metric_values
        assert f"{updated_metric_value:.4f}" in returned_metric_values

    @pytest.mark.django_db
    def test_multiple_data_points_with_sequential_refresh_dates_can_be_ingested(
        self,
        example_headline_data: INCOMING_DATA_TYPE,
        timestamp_2_months_from_now: datetime.datetime,
    ):
        """
        Given 3 headline data points with sequential `refresh_dates`
        When the files are uploaded via the `data_ingester()`
        Then the headlines/ endpoint will always return the latest-functional data
        And stale records will be deleted throughout the process
        """
        # The fixture comes bundled with 2 data points.
        # To keep things simple we get rid of the 2nd data point
        example_headline_data["data"].pop(1)

        headlines_endpoint_payload = {
            "topic": example_headline_data["topic"],
            "metric": example_headline_data["metric"],
            "geography": example_headline_data["geography"],
            "geography_type": example_headline_data["geography_type"],
            "sex": example_headline_data["sex"],
            "age": example_headline_data["age"],
            "stratum": example_headline_data["stratum"],
        }

        # Given
        first_metric_value = 123
        first_refresh_date = "2023-12-01"
        first_headline_data = copy.deepcopy(example_headline_data)
        first_headline_data["refresh_date"] = first_refresh_date
        first_headline_data["data"][0]["upper_confidence"] = first_metric_value + 1
        first_headline_data["data"][0]["metric_value"] = first_metric_value
        first_headline_data["data"][0]["lower_confidence"] = first_metric_value - 1
        data_ingester(data=first_headline_data)
        assert CoreHeadline.objects.all().count() == 1

        # When / Then
        current_headline_from_api = self._fetch_latest_headline_from_endpoint(
            payload=headlines_endpoint_payload
        )
        assert current_headline_from_api["value"] == first_metric_value

        # Given
        second_metric_value = 456
        second_refresh_date = "2023-12-01 13:00:00"
        second_headline_data = copy.deepcopy(example_headline_data)
        second_headline_data["refresh_date"] = second_refresh_date
        second_headline_data["data"][0]["upper_confidence"] = second_metric_value + 1
        second_headline_data["data"][0]["metric_value"] = second_metric_value
        second_headline_data["data"][0]["lower_confidence"] = second_metric_value - 1
        data_ingester(data=second_headline_data)
        assert CoreHeadline.objects.all().count() == 2

        # When / Then
        current_headline_from_api = self._fetch_latest_headline_from_endpoint(
            payload=headlines_endpoint_payload
        )
        assert current_headline_from_api["value"] == second_metric_value

        # Given
        third_metric_value = 756
        third_refresh_date = "2023-12-01 13:01:00"
        third_headline_data = copy.deepcopy(example_headline_data)
        third_headline_data["refresh_date"] = third_refresh_date
        third_headline_data["data"][0]["upper_confidence"] = third_metric_value + 1
        third_headline_data["data"][0]["metric_value"] = third_metric_value
        third_headline_data["data"][0]["lower_confidence"] = third_metric_value - 1
        data_ingester(data=third_headline_data)

        # When
        current_headline_from_api = self._fetch_latest_headline_from_endpoint(
            payload=headlines_endpoint_payload
        )

        # Then
        # The returned live value from the headlines API should be the latest one
        assert current_headline_from_api["value"] == third_metric_value

        assert CoreHeadline.objects.all().count() == 2
        all_headline_metric_values = CoreHeadline.objects.all().values_list(
            "metric_value", flat=True
        )

        # The value associated with the stale record should have been deleted
        assert first_metric_value not in all_headline_metric_values

        # The live record and the 1 leftover stale record should be in the db.
        # Because we clear stale records before ingestion,
        # the leftover stale record would be deleted
        # before the next hypothetical ingestion round
        assert second_metric_value in all_headline_metric_values
        assert third_metric_value in all_headline_metric_values

    @pytest.mark.django_db
    def test_data_point_can_be_updated_and_then_set_to_original_value(
        self,
        example_headline_data: INCOMING_DATA_TYPE,
        timestamp_2_months_from_now: datetime.datetime,
    ):
        """
        Given 3 headline data points with sequential `refresh_dates`
        Which result in the 1st metric value being set in the final round
        When the files are uploaded via the `data_ingester()`
        Then the stale record will be deleted throughout the process
        """
        # The fixture comes bundled with 2 data points.
        # To keep things simple we get rid of the 2nd data point
        example_headline_data["data"].pop(1)

        # Given
        first_metric_value = Decimal("123.0000")
        first_refresh_date = datetime.datetime(
            year=2023, month=12, day=1, tzinfo=datetime.UTC
        )
        first_headline_data = copy.deepcopy(example_headline_data)
        first_headline_data["refresh_date"] = first_refresh_date
        first_headline_data["data"][0]["upper_confidence"] = first_metric_value + 1
        first_headline_data["data"][0]["metric_value"] = first_metric_value
        first_headline_data["data"][0]["lower_confidence"] = first_metric_value - 1

        # When
        data_ingester(data=first_headline_data)

        # Then
        assert CoreHeadline.objects.all().count() == 1

        # Given
        second_metric_value = Decimal("456.0000")
        second_refresh_date = datetime.datetime(
            year=2023, month=12, day=2, tzinfo=datetime.UTC
        )
        second_headline_data = copy.deepcopy(example_headline_data)
        second_headline_data["refresh_date"] = second_refresh_date
        second_headline_data["data"][0]["upper_confidence"] = second_metric_value + 1
        second_headline_data["data"][0]["metric_value"] = second_metric_value
        second_headline_data["data"][0]["lower_value"] = second_metric_value - 1

        # When
        data_ingester(data=second_headline_data)

        # Then
        # At this point the first metric value `123` isn't considered stale
        assert CoreHeadline.objects.all().count() == 2

        # Given
        third_refresh_date = datetime.datetime(
            year=2023, month=12, day=3, tzinfo=datetime.UTC
        )
        third_headline_data = copy.deepcopy(example_headline_data)
        third_headline_data["refresh_date"] = third_refresh_date
        third_headline_data["data"][0]["upper_confidence"] = first_metric_value + 1
        third_headline_data["data"][0]["metric_value"] = first_metric_value
        third_headline_data["data"][0]["lower_value"] = first_metric_value - 1

        # When
        data_ingester(data=third_headline_data)

        # Then
        # At this point the first metric value `123` is now considered stale
        assert CoreHeadline.objects.all().count() == 2
        all_headline_metric_values = CoreHeadline.objects.all().values_list(
            "metric_value", "refresh_date"
        )
        assert (first_metric_value, third_refresh_date) in all_headline_metric_values
        assert (second_metric_value, second_refresh_date) in all_headline_metric_values
        assert (
            first_metric_value,
            first_refresh_date,
        ) not in all_headline_metric_values

    @staticmethod
    def _fetch_latest_headline_from_endpoint(
        payload: dict[str, str],
    ) -> dict[str, int | float]:
        path = "/api/headlines/v3/"
        client = APIClient()
        response: Response = client.get(path=path, data=payload)
        return response.data

    @staticmethod
    def _rebuild_data_with_updated_refresh_date_only(
        data: INCOMING_DATA_TYPE,
        refresh_date: datetime.date,
    ) -> INCOMING_DATA_TYPE:
        sample_data_with_no_functional_updates = data.copy()
        sample_data_with_no_functional_updates["refresh_date"] = str(refresh_date)
        return sample_data_with_no_functional_updates

    def _rebuild_data_with_single_retrospective_update(
        self,
        data: INCOMING_DATA_TYPE,
        refresh_date: datetime.date,
        metric_value: float,
    ) -> INCOMING_DATA_TYPE:
        sample_data_with_one_retrospective_update = (
            self._rebuild_data_with_updated_refresh_date_only(
                data=data,
                refresh_date=refresh_date,
            )
        )
        sample_data_with_one_retrospective_update["time_series"][0][
            "metric_value"
        ] = metric_value
        return sample_data_with_one_retrospective_update

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
