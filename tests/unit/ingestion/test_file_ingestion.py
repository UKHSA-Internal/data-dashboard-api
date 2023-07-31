from unittest import mock

from ingestion.consumer import Consumer
from ingestion.file_ingestion import file_ingester
import pytest


class TestFileIngester:
    @mock.patch.object(Consumer, "create_headlines")
    def test_delegates_call_to_create_headlines_for_headline_data(self, spy_create_headlines: mock.MagicMock):
        """
        Given a file which has `headline` in the filename
        When `file_ingester` is called
        Then the call is delegated to the `create_headlines()` method
            on an instance of `Consumer`
        """
        # Given
        mocked_file = mock.Mock()
        mocked_file.name = "some_headline_file.json"

        # When
        file_ingester(file=mocked_file)

        # Then
        spy_create_headlines.assert_called_once()

    @mock.patch.object(Consumer, "create_timeseries")
    def test_delegates_call_to_create_timeseries_for_timeseries_data(self, spy_create_timeseries: mock.MagicMock):
        """
        Given a file which has `headline` in the filename
        When `file_ingester` is called
        Then the call is delegated to the `create_timeseries()` method
            on an instance of `Consumer`
        """
        # Given
        mocked_file = mock.Mock()
        mocked_file.name = "some_timeseries_file.json"

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
