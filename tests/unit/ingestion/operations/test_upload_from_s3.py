from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from ingestion.file_ingestion import FileIngestionFailedError
from ingestion.operations.upload_from_s3 import (
    _upload_file_and_remove_local_copy,
    download_file_ingest_and_teardown,
    download_files_and_upload,
    ingest_data_and_post_process,
)

MODULE_PATH = "ingestion.operations.upload_from_s3"
FAKE_FILENAME = "abc.json"


class TestDownloadFilesAndUpload:
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_delegates_call_to_clear_metrics_tables(
        self, spy_clear_metrics_tables: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object
        When `download_files_and_upload()` is called
        Then `clear_metrics_tables()` is called

        Patches:
            `spy_clear_metrics_tables`: For the main assertion
                of checking the metrics tables are cleared

        """
        # Given
        mocked_client = mock.MagicMock()

        # When
        download_files_and_upload(client=mocked_client)

        # Then
        spy_clear_metrics_tables.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.download_file_ingest_and_teardown")
    @mock.patch(f"{MODULE_PATH}.run_with_multiple_processes")
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_delegates_calls_for_each_key_of_item_in_folder(
        self,
        mocked_clear_metrics_tables: mock.MagicMock,
        spy_run_with_multiple_processes: mock.MagicMock,
        spy_download_file_ingest_and_teardown: mock.MagicMock,
    ):
        """
        Given a mocked `AWSClient` object
        When `download_files_and_upload()` is called
        Then `run_with_multiple_processes()` is called
            with the correct callable
            and iterable for each key listed from the client

        Patches:
            `mocked_clear_metrics_tables`: To remove the
                side effects of having to delete records
                from the database
            `spy_download_file_ingest_and_teardown`: To check
                the callable is passed to the
                `run_with_multiple_processes` call
            `spy_run_with_multiple_processes`: For the
                main assertion.

        """
        # Given
        mocked_client = mock.MagicMock()
        fake_keys = [FAKE_FILENAME, "xyz.json"]
        mocked_client.list_item_keys_of_in_folder.return_value = fake_keys

        # When
        download_files_and_upload(client=mocked_client)

        # Then
        spy_run_with_multiple_processes.assert_called_once_with(
            upload_function=spy_download_file_ingest_and_teardown,
            items=fake_keys,
        )

    @mock.patch(f"{MODULE_PATH}.run_with_multiple_processes")
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_records_log_statement_for_completion(
        self,
        mocked_clear_metrics_tables: mock.MagicMock,
        mocked_run_with_multiple_processes: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given a mocked `AWSClient` object
        When `download_files_and_upload()` is called
        Then the correct log is recorded

        Patches:
            `mocked_clear_metrics_tables`: To remove the
                side effects of having to delete records
                from the database
            `mocked_run_with_multiple_processes`: To remove
                side effects of having to create multiple processes
                and upload to the database

        """
        # Given
        mocked_client = mock.MagicMock()
        mocked_client.list_item_keys_of_in_folder.return_value = []

        # When
        download_files_and_upload(client=mocked_client)

        # Then
        assert "Completed dataset upload" in caplog.text


class TestDownloadFileIngestAndTeardown:
    @mock.patch(f"{MODULE_PATH}._upload_file_and_remove_local_copy")
    def test_delegates_call_to_download_item(
        self, mocked_upload_file_and_remove_local_copy: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        When `download_file_ingest_and_teardown()` is called
        Then `download_item()` is called from the client

        Patches:
            `mocked_upload_file_and_remove_local_copy`: To remove
                the side effects of opening & ingesting the file

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME

        # When
        download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        spy_client.download_item.assert_called_once_with(key=fake_key)

    @mock.patch(f"{MODULE_PATH}._upload_file_and_remove_local_copy")
    def test_delegates_call_to_upload_file_and_remove_local_copy(
        self, spy_upload_file_and_remove_local_copy: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        When `download_file_ingest_and_teardown()` is called
        Then `_upload_file_and_remove_local_copy()` is called

        Patches:
            `spy_upload_file_and_remove_local_copy`: For the
                main assertion of checking the downloaded file
                is passed to this function call

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME

        # When
        download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        downloaded_item_filepath = spy_client.download_item.return_value
        spy_upload_file_and_remove_local_copy.assert_called_once_with(
            filepath=downloaded_item_filepath
        )

    @mock.patch(f"{MODULE_PATH}._upload_file_and_remove_local_copy")
    def test_delegates_call_to_move_file_to_processed_folder_for_successful_upload(
        self, mocked_upload_file_and_remove_local_copy: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        When `download_file_ingest_and_teardown()` is called
        Then `move_file_to_processed_folder()` is called from the client

        Patches:
            `mocked_upload_file_and_remove_local_copy`: To remove
                the side effects of opening & ingesting the file

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME

        # When
        download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        spy_client.move_file_to_processed_folder.assert_called_once_with(key=fake_key)
        spy_client.move_file_to_failed_folder.assert_not_called()

    @mock.patch(f"{MODULE_PATH}._upload_file_and_remove_local_copy")
    def test_calls_move_file_to_failed_folder_if_error_is_raised(
        self, mocked_upload_file_and_remove_local_copy: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        And a file upload which will raise a `FileIngestionFailedError`
        When `download_file_ingest_and_teardown()` is called
        Then `move_file_to_failed_folder()` is called from the client

        Patches:
            `mocked_upload_file_and_remove_local_copy`: To simulate
                the file upload failing

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME
        mocked_upload_file_and_remove_local_copy.side_effect = [
            FileIngestionFailedError(file_name=fake_key)
        ]

        # When
        download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        spy_client.move_file_to_failed_folder.assert_called_once_with(key=fake_key)
        spy_client.move_file_to_processed_folder.assert_not_called()


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
    @mock.patch(f"{MODULE_PATH}._upload_file")
    def test_delegates_call_to_upload_file(
        self,
        spy_upload_file: mock.MagicMock,
        mocked_os_remove: mock.MagicMock,
    ):
        """
        Given a fake file path
        When `_upload_file_and_remove_local_copy()` is called
        Then the call is delegated to `_upload_file()`

        Patches:
            `spy_upload_file`: For the main assertion
            `mocked_os_remove`: To remove the side effect
                of having to remove a non-existent file on disk

        """
        # Given
        fake_filepath = FAKE_FILENAME

        # When
        _upload_file_and_remove_local_copy(filepath=fake_filepath)

        # Then
        spy_upload_file.assert_called_once_with(filepath=fake_filepath)

    @mock.patch(f"{MODULE_PATH}.os.remove")
    @mock.patch(f"{MODULE_PATH}._upload_file")
    def test_calls_os_remove_to_remove_file(
        self,
        mocked_upload_file: mock.MagicMock,
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
        spy_os_remove.assert_called_once_with(path=fake_filepath)

    @mock.patch(f"{MODULE_PATH}.os.remove")
    @mock.patch(f"{MODULE_PATH}._upload_file")
    def test_calls_os_remove_to_remove_file_when_error_is_raised(
        self,
        mocked_upload_file: mock.MagicMock,
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
        mocked_upload_file.side_effect = [
            FileIngestionFailedError(file_name=fake_filepath)
        ]

        # When
        with pytest.raises(FileIngestionFailedError):
            _upload_file_and_remove_local_copy(filepath=fake_filepath)

        # Then
        spy_os_remove.assert_called_once_with(path=fake_filepath)
