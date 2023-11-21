from unittest import mock

import pytest

from ingestion.consumer import Consumer
from ingestion.file_ingestion import data_ingester, file_ingester
from ingestion.utils import type_hints
from ingestion.utils.enums import DataSourceFileType
from ingestion.v2.consumer import ConsumerV2


class TestFileIngester:
    @mock.patch.object(Consumer, "create_headlines")
    def test_delegates_call_to_create_headlines_for_headline_data(
        self, spy_create_headlines: mock.MagicMock
    ):
        """
        Given a file which has `headline` in the filename
        When `file_ingester` is called
        Then the call is delegated to the `create_headlines()` method
            on an instance of `Consumer`
        """
        # Given
        mocked_file = mock.Mock()
        mocked_file.name = "COVID-19_headline_positivity_latest.json"

        # When
        file_ingester(file=mocked_file)

        # Then
        spy_create_headlines.assert_called_once()

    @pytest.mark.parametrize(
        "file_name_section",
        [
            DataSourceFileType.cases.value,
            DataSourceFileType.deaths.value,
            DataSourceFileType.healthcare.value,
            DataSourceFileType.testing.value,
            DataSourceFileType.vaccinations.value,
        ],
    )
    @mock.patch.object(Consumer, "create_timeseries")
    def test_delegates_call_to_create_timeseries_for_timeseries_data(
        self,
        spy_create_timeseries: mock.MagicMock,
        file_name_section: str,
    ):
        """
        Given a file which has `headline` in the filename
        When `file_ingester` is called
        Then the call is delegated to the `create_timeseries()` method
            on an instance of `Consumer`
        """
        # Given
        mocked_file = mock.Mock()
        mocked_file.name = f"COVID-19_{file_name_section}_Latest.json"

        # When
        file_ingester(file=mocked_file)

        # Then
        spy_create_timeseries.assert_called_once()

    def test_raises_error_for_invalid_file(self):
        """
        Given an invalid file which does not have
            a recognizable keyword in the filename
        When `file_ingester` is called
        Then a `ValueError` is raised
        """
        # Given
        mocked_file = mock.Mock()
        mocked_file.name = "some_invalid_file.json"

        # When / Then
        with pytest.raises(ValueError):
            file_ingester(file=mocked_file)


class TestDataIngester:
    @mock.patch.object(ConsumerV2, "create_core_and_api_timeseries")
    @mock.patch.object(ConsumerV2, "create_core_headlines")
    def test_delegates_call_to_create_headlines_for_headline_data(
        self,
        spy_create_core_headlines: mock.MagicMock,
        spy_create_core_and_api_timeseries: mock.MagicMock,
        example_headline_data_v2: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given data which has a "metric_group" value of "headline"
        When `data_ingester` is called
        Then the call is delegated to the
            `create_core_headlines()` method
            on an instance of `Consumer`
        """
        # Given
        fake_data = {"metric_group": DataSourceFileType.headline.value}

        # When
        data_ingester(data=fake_data)

        # Then
        spy_create_core_headlines.assert_called_once()
        spy_create_core_and_api_timeseries.assert_not_called()

    @pytest.mark.parametrize(
        "metric_group",
        [
            DataSourceFileType.cases.value,
            DataSourceFileType.deaths.value,
            DataSourceFileType.healthcare.value,
            DataSourceFileType.testing.value,
            DataSourceFileType.vaccinations.value,
        ],
    )
    @mock.patch.object(ConsumerV2, "create_core_headlines")
    @mock.patch.object(ConsumerV2, "create_core_and_api_timeseries")
    def test_delegates_call_to_create_timeseries_for_timeseries_data(
        self,
        spy_create_core_and_api_timeseries: mock.MagicMock,
        spy_create_core_headlines: mock.MagicMock,
        metric_group: str,
        example_time_series_data_v2: type_hints.INCOMING_DATA_TYPE,
    ):
        """
        Given data which has a "metric_group" value other than "headline"
        When `data_ingester` is called
        Then the call is delegated to the
            `create_core_and_api_timeseries()` method
            on an instance of `Consumer`
        """
        # Given
        fake_data = {"metric_group": metric_group}

        # When
        data_ingester(data=fake_data)

        # Then
        spy_create_core_and_api_timeseries.assert_called_once()
        spy_create_core_headlines.assert_not_called()
