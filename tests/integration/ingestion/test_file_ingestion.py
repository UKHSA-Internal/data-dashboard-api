import copy
import zoneinfo

import pytest

from ingestion.file_ingestion import data_ingester
from ingestion.utils import type_hints
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries

EXPECTED_DATE_FORMAT = "%Y-%m-%d"


class TestDataIngester:
    @pytest.mark.django_db
    def test_creates_core_headlines_from_data(
        self, example_headline_data: type_hints.INCOMING_DATA_TYPE
    ):
        """
        Given incoming headline type data
        When `data_ingester()` is called
        Then `CoreHeadline` records are created with the correct values
        """
        # Given
        data = example_headline_data
        assert CoreHeadline.objects.all().count() == 0

        # When
        data_ingester(data=data)

        # Then
        # Check that 2 `CoreHeadline` records are created per row of data
        assert CoreHeadline.objects.all().count() == len(example_headline_data["data"])
        core_headline = CoreHeadline.objects.first()

        assert core_headline.metric.topic.sub_theme.theme.name == data["parent_theme"]
        assert core_headline.metric.topic.sub_theme.name == data["child_theme"]
        assert core_headline.metric.topic.name == data["topic"]
        assert core_headline.metric.metric_group.name == data["metric_group"]
        assert core_headline.metric.name == data["metric"]

        assert core_headline.geography.name == data["geography"]
        assert core_headline.geography.geography_code == data["geography_code"]
        assert core_headline.geography.geography_type.name == data["geography_type"]

        assert core_headline.age.name == data["age"]
        assert core_headline.stratum.name == data["stratum"]
        assert core_headline.sex == data["sex"]
        assert core_headline.refresh_date.strftime("%Y-%m-%d") == data["refresh_date"]

        london_timezone = zoneinfo.ZoneInfo(key="Europe/London")
        assert (
            core_headline.period_start.astimezone(tz=london_timezone).strftime(
                EXPECTED_DATE_FORMAT
            )
            == data["data"][0]["period_start"]
        )
        assert (
            core_headline.period_end.astimezone(tz=london_timezone).strftime(
                EXPECTED_DATE_FORMAT
            )
            == data["data"][0]["period_end"]
        )
        assert str(round(core_headline.metric_value, 1)) == str(
            data["data"][0]["metric_value"]
        )
        # The embargo timestamp specifies the point in time up to the second
        assert (
            core_headline.embargo.strftime("%Y-%m-%d %H:%M:%S")
            == data["data"][0]["embargo"]
        )

    @pytest.mark.django_db
    def test_creates_core_time_series_from_data(
        self, example_time_series_data: type_hints.INCOMING_DATA_TYPE
    ):
        """
        Given incoming time series type data
        When `data_ingester()` is called
        Then `CoreTimeSeries` records are created with the correct values
        """
        # Given
        data = example_time_series_data
        assert CoreTimeSeries.objects.all().count() == 0

        # When
        data_ingester(data=data)

        # Then
        # Check that 1 `CoreTimeSeries` record is created per row of data
        assert CoreTimeSeries.objects.all().count() == len(
            example_time_series_data["time_series"]
        )
        core_time_series = CoreTimeSeries.objects.first()

        assert (
            core_time_series.metric.topic.sub_theme.theme.name == data["parent_theme"]
        )
        assert core_time_series.metric.topic.sub_theme.name == data["child_theme"]
        assert core_time_series.metric.topic.name == data["topic"]
        assert core_time_series.metric.metric_group.name == data["metric_group"]
        assert core_time_series.metric.name == data["metric"]

        assert core_time_series.geography.name == data["geography"]
        assert core_time_series.geography.geography_code == data["geography_code"]
        assert core_time_series.geography.geography_type.name == data["geography_type"]

        assert core_time_series.age.name == data["age"]
        assert core_time_series.stratum.name == data["stratum"]
        assert core_time_series.sex == data["sex"]
        assert (
            core_time_series.refresh_date.strftime("%Y-%m-%d") == data["refresh_date"]
        )

        assert str(core_time_series.date) == data["time_series"][0]["date"]
        assert round(core_time_series.epiweek, 2) == round(
            data["time_series"][0]["epiweek"], 2
        )
        assert str(round(core_time_series.metric_value, 2)) == str(
            round(data["time_series"][0]["metric_value"], 2)
        )
        # The embargo timestamp specifies the point in time up to the second
        assert (
            core_time_series.embargo.strftime("%Y-%m-%d %H:%M:%S")
            == data["time_series"][0]["embargo"]
        )
        assert core_time_series.in_reporting_delay_period is False

    @pytest.mark.django_db
    def test_creates_api_time_series_from_data(
        self, example_time_series_data: type_hints.INCOMING_DATA_TYPE
    ):
        """
        Given incoming time series type data
        When `data_ingester()` is called
        Then `APITimeSeries` records are created with the correct values
        """
        # Given
        data = example_time_series_data
        assert APITimeSeries.objects.all().count() == 0

        # When
        data_ingester(data=data)

        # Then
        # Check that 1 `APITimeSeries` record is created per row of data
        assert APITimeSeries.objects.all().count() == len(
            example_time_series_data["time_series"]
        )
        core_time_series = APITimeSeries.objects.first()

        assert core_time_series.theme == data["parent_theme"]
        assert core_time_series.sub_theme == data["child_theme"]
        assert core_time_series.topic == data["topic"]
        assert core_time_series.metric_group == data["metric_group"]
        assert core_time_series.metric == data["metric"]

        assert core_time_series.geography == data["geography"]
        assert core_time_series.geography_code == data["geography_code"]
        assert core_time_series.geography_type == data["geography_type"]

        assert core_time_series.age == data["age"]
        assert core_time_series.stratum == data["stratum"]
        assert core_time_series.sex == data["sex"]
        assert (
            core_time_series.refresh_date.strftime("%Y-%m-%d") == data["refresh_date"]
        )

        assert (
            core_time_series.date.strftime("%Y-%m-%d") == data["time_series"][0]["date"]
        )
        assert core_time_series.epiweek == data["time_series"][0]["epiweek"]
        assert core_time_series.metric_value == data["time_series"][0]["metric_value"]
        # The embargo timestamp specifies the point in time up to the second
        assert (
            core_time_series.embargo.strftime("%Y-%m-%d %H:%M:%S")
            == data["time_series"][0]["embargo"]
        )

    @pytest.mark.django_db
    def test_updates_api_timeseries_embargo_date(
        self,
        example_time_series_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given time series data ingested once
        When the same data is ingested again with a later refresh date
            and an updated embargo timestamp
        Then the latest records for CoreTimeSeries and APITimeSeries
            reflect the updated embargo timestamps
        """

        # Before ingestion
        assert CoreTimeSeries.objects.all().count() == 0
        assert APITimeSeries.objects.all().count() == 0

        # Given
        initial_timeseries_data = copy.deepcopy(example_time_series_data)
        updated_timeseries_data = copy.deepcopy(initial_timeseries_data)

        # When
        data_ingester(data=initial_timeseries_data)

        # Reingest with updated embargo and later refresh date
        updated_timeseries_refresh_date = "2023-11-21"
        updated_timeseries_embargo = "2023-11-19 09:15:00"

        updated_timeseries_data["refresh_date"] = updated_timeseries_refresh_date
        for record in updated_timeseries_data["time_series"]:
            record["embargo"] = updated_timeseries_embargo

        data_ingester(data=updated_timeseries_data)

        # Then
        updated_core_timeseries = CoreTimeSeries.objects.filter(
            refresh_date__date=updated_timeseries_refresh_date
        )
        assert len(updated_timeseries_data["time_series"]) == 2
        for record in updated_core_timeseries:
            assert (
                record.embargo.strftime("%Y-%m-%d %H:%M:%S")
                == updated_timeseries_embargo
            )

        updated_api_timeseries = APITimeSeries.objects.filter(
            refresh_date__date=updated_timeseries_refresh_date
        )
        assert updated_api_timeseries.count() == len(
            updated_timeseries_data["time_series"]
        )
        for record in updated_api_timeseries:
            assert (
                record.embargo.strftime("%Y-%m-%d %H:%M:%S")
                == updated_timeseries_embargo
            )

    @pytest.mark.django_db
    def test_updates_api_coreheadline_embargo_date(
        self,
        example_headline_data: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given headline data ingested once
        When the same data is ingested again with a later refresh date
            and an updated embargo timestamp
        Then the latest record for CoreHeadline
            reflect the updated embargo timestamps
        """

        # Before ingestion
        assert CoreHeadline.objects.all().count() == 0

        # Given
        initial_headline_data = copy.deepcopy(example_headline_data)
        updated_headline_data = copy.deepcopy(initial_headline_data)

        # When
        data_ingester(data=initial_headline_data)

        # Reingest with updated embargo and later refresh date
        updated_headline_refresh_date = "2023-11-21"
        updated_headline_embargo = "2023-11-18 08:00:00"

        updated_headline_data["refresh_date"] = updated_headline_refresh_date
        for record in updated_headline_data["data"]:
            record["embargo"] = updated_headline_embargo

        data_ingester(data=updated_headline_data)

        # Then
        updated_headlines = CoreHeadline.objects.filter(
            refresh_date__date=updated_headline_refresh_date
        )
        assert len(updated_headline_data["data"]) == 2
        for record in updated_headlines:
            assert (
                record.embargo.strftime("%Y-%m-%d %H:%M:%S") == updated_headline_embargo
            )
