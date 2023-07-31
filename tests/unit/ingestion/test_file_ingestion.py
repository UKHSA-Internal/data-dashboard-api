from unittest import mock

import pytest

from ingestion.consumer import Consumer
from ingestion.file_ingestion import DataSourceFileType, file_ingester


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
