from pathlib import Path
from unittest import mock

import pytest

from ingestion.file_ingestion import FileIngestionFailedError
from ingestion.operations.upload import (
    _upload_file_and_remove_local_copy,
    ingest_data_and_post_process,
)

MODULE_PATH = "ingestion.operations.upload"
FAKE_FILENAME = "abc.json"


class TestIngestDataAndPostProcess:
    @mock.patch(f"{MODULE_PATH}.upload_data")
    def test_delegates_call_to_upload_data(self, spy_upload_data: mock.MagicMock):
        """
        Given a mocked `AWSClient` object and a fake item key & data
        When `ingest_data_and_post_process()` is called
        Then `upload_data()` is called

        Patches:
            `spy_upload_data`: For the main assertion of
                checking the data is passed to this function call

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME
        fake_data = mock.Mock()

        # When
        ingest_data_and_post_process(data=fake_data, key=fake_key, client=spy_client)

        # Then
        spy_upload_data.assert_called_once_with(data=fake_data, key=fake_key)

    @mock.patch(f"{MODULE_PATH}.upload_data")
    def test_delegates_call_to_move_file_to_processed_folder_for_successful_upload(
        self, mocked_upload_data: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key & data
        When `ingest_data_and_post_process()` is called
        Then `upload_data()` is called

        Patches:
            `mocked_upload_data`: To remove the side effects
                of having to ingest the file

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME
        fake_data = mock.Mock()

        # When
        ingest_data_and_post_process(data=fake_data, key=fake_key, client=spy_client)

        # Then
        spy_client.move_file_to_processed_folder.assert_called_once_with(key=fake_key)
        spy_client.move_file_to_failed_folder.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.upload_data")
    def test_delegates_call_to_move_file_to_failed_folder_if_error_is_raised(
        self, mocked_upload_data: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        And a file upload which will raise a `FileIngestionFailedError`
        When `ingest_data_and_post_process()` is called
        Then `move_file_to_failed_folder()` is called from the client

        Patches:
            `mocked_upload_data`: To simulate
                the file upload failing

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME
        fake_data = mock.Mock()
        mocked_upload_data.side_effect = [FileIngestionFailedError(file_name=fake_key)]

        # When
        ingest_data_and_post_process(data=fake_data, key=fake_key, client=spy_client)

        # Then
        spy_client.move_file_to_failed_folder.assert_called_once_with(key=fake_key)
        spy_client.move_file_to_processed_folder.assert_not_called()


class TestUploadFileAndRemoveLocalCopy:
    @mock.patch(f"{MODULE_PATH}.os.remove")
    @mock.patch(f"{MODULE_PATH}._upload_data_as_file")
    def test_delegates_call_to_upload_file(
        self,
        spy_upload_data_as_file: mock.MagicMock,
        mocked_os_remove: mock.MagicMock,
    ):
        """
        Given a fake file path
        When `_upload_file_and_remove_local_copy()` is called
        Then the call is delegated to `_upload_file()`

        Patches:
            `spy_upload_data_as_file`: For the main assertion
            `mocked_os_remove`: To remove the side effect
                of having to remove a non-existent file on disk

        """
        # Given
        fake_filepath = FAKE_FILENAME

        # When
        _upload_file_and_remove_local_copy(filepath=fake_filepath)

        # Then
        spy_upload_data_as_file.assert_called_once_with(filepath=Path(fake_filepath))

    @mock.patch(f"{MODULE_PATH}.os.remove")
    @mock.patch(f"{MODULE_PATH}._upload_data_as_file")
    def test_calls_os_remove_to_remove_file(
        self,
        mocked_upload_data_as_file: mock.MagicMock,
        spy_os_remove: mock.MagicMock,
    ):
        """
        Given a fake file path
        When `_upload_file_and_remove_local_copy()` is called
        Then the call is delegated to `os.remove`

        Patches:
            `mocked_upload_file`: To remove the side effect
                of having to ingest and open a non-existent file
            `spy_os_remove`: For the main assertion to check
                that the filesystem is cleared

        """
        # Given
        fake_filepath = FAKE_FILENAME

        # When
        _upload_file_and_remove_local_copy(filepath=fake_filepath)

        # Then
        spy_os_remove.assert_called_once_with(path=Path(fake_filepath))

    @mock.patch(f"{MODULE_PATH}.os.remove")
    @mock.patch(f"{MODULE_PATH}._upload_data_as_file")
    def test_calls_os_remove_to_remove_file_when_error_is_raised(
        self,
        mocked_upload_data_as_file: mock.MagicMock,
        spy_os_remove: mock.MagicMock,
    ):
        """
        Given a fake file path which will fail upon upload
        When `_upload_file_and_remove_local_copy()` is called
        Then the call is delegated to `os.remove`
            despite the `FileIngestionFailedError` being raised

        Patches:
            `mocked_upload_file`: To simulate the file upload failing
            `spy_os_remove`: For the main assertion to check
                that the filesystem is cleared

        """
        # Given
        fake_filepath = FAKE_FILENAME
        mocked_upload_data_as_file.side_effect = [
            FileIngestionFailedError(file_name=fake_filepath)
        ]

        # When
        with pytest.raises(FileIngestionFailedError):
            _upload_file_and_remove_local_copy(filepath=fake_filepath)

        # Then
        spy_os_remove.assert_called_once_with(path=Path(fake_filepath))
