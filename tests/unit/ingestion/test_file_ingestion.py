from pathlib import Path
from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from ingestion.consumer import Consumer
from ingestion.file_ingestion import (
    DataSourceFileType,
    FileIngestionFailedError,
    _open_data_from_file,
    _upload_data_as_file,
    data_ingester,
    file_ingester,
    upload_data,
)
from ingestion.v2.consumer import ConsumerV2

MODULE_PATH = "ingestion.file_ingestion"


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


class TestUploadData:
    @mock.patch(f"{MODULE_PATH}.data_ingester")
    def test_delegates_call_to_data_ingester(
        self, spy_data_ingester: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given mocked data and a file key
        When `upload_data()` is called
        Then the call is delegated to `data_ingester()`
        And the correct logs are made

        Patches:
            `spy_data_ingester`: For the main assertion

        """
        # Given
        mocked_key = mock.Mock()
        mocked_data = mock.Mock()

        # When
        upload_data(key=mocked_key, data=mocked_data)

        # Then
        spy_data_ingester.assert_called_once_with(data=mocked_data)
        assert f"Uploading {mocked_key}" in caplog.text
        assert f"Completed ingestion of {mocked_key}" in caplog.text

    @mock.patch(f"{MODULE_PATH}.data_ingester")
    def test_raises_error_with_correct_log_statement(
        self, mocked_data_ingester: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given mocked data and a file key
        When `upload_data()` is called
        Then the call is delegated to `data_ingester()`
        And the correct logs are made

        Patches:
            `mocked_data_ingester`: To simulate an error
                being thrown during the data ingestion

        """
        # Given
        mocked_key = mock.Mock()
        mocked_data = mock.Mock()
        error = Exception()
        mocked_data_ingester.side_effect = [error]

        # When / Then
        with pytest.raises(FileIngestionFailedError):
            upload_data(key=mocked_key, data=mocked_data)

            assert f"Failed upload of {mocked_key} due to {error}" in caplog.text


class TestUploadDataAsFile:
    @mock.patch(f"{MODULE_PATH}.upload_data")
    @mock.patch(f"{MODULE_PATH}._open_data_from_file")
    @mock.patch("builtins.open")
    def test_opens_file_and_delegates_to_upload_data(
        self,
        mocked_open: mock.MagicMock,
        spy_open_data_from_file: mock.MagicMock,
        spy_upload_data: mock.MagicMock,
    ):
        """
        Given a fake file
        When `_upload_data_as_file()` is called
        Then the call is delegated to open the data from the file
        And then to pass it to the call to the `upload_data`()` function

        Patches:
            `mocked_open`: To prevent the side effects of having
                to open a real file from the local filesystem
            `spy_open_data_from_file`: To check the opened
                file is passed to this function for the data
                to be extracted as a dict
            `spy_upload_data`: For the main assertion

        """
        # Given
        fake_path = Path("abc.json")

        # When
        _upload_data_as_file(filepath=fake_path)

        # Then
        spy_open_data_from_file.assert_called_with(
            file=mocked_open.return_value.__enter__.return_value
        )
        spy_upload_data.assert_called_once_with(
            key=fake_path.name, data=spy_open_data_from_file.return_value
        )


class TestOpenDataFromFile:
    @mock.patch(f"{MODULE_PATH}.json")
    def test_delegates_calls_successfully(self, spy_json: mock.MagicMock):
        """
        Given a mocked file object
        When `_open_data_from_file()` is called
        Then the call is delegated to read the file
            and to pass it to the call to be deserialized
        """
        # Given
        mocked_file = mock.MagicMock()

        # When
        _open_data_from_file(file=mocked_file)

        # Then
        mocked_file.readlines.assert_called_once()
        spy_json.loads.assert_called_once_with(mocked_file.readlines.return_value[0])
