from unittest import mock

from _pytest.logging import LogCaptureFixture

from ingestion.operations.upload_from_s3 import (
    _download_file_ingest_and_teardown,
    _upload_file_and_remove_local_copy,
    download_files_and_upload,
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

    @mock.patch(f"{MODULE_PATH}._download_file_ingest_and_teardown")
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_delegates_calls_for_each_key_of_item_in_folder(
        self,
        mocked_clear_metrics_tables: mock.MagicMock,
        spy_download_file_ingest_and_teardown: mock.MagicMock,
    ):
        """
        Given a mocked `AWSClient` object
        When `download_files_and_upload()` is called
        Then `_download_file_ingest_and_teardown()` is called
            for each key listed from the client

        Patches:
            `mocked_clear_metrics_tables`: To remove the
                side effects of having to delete records
                from the database

        """
        # Given
        mocked_client = mock.MagicMock()
        fake_keys = [FAKE_FILENAME, "xyz.json"]
        mocked_client.list_item_keys_of_in_folder.return_value = fake_keys

        # When
        download_files_and_upload(client=mocked_client)

        # Then
        expected_calls = [
            mock.call(key=fake_key, client=mocked_client) for fake_key in fake_keys
        ]
        spy_download_file_ingest_and_teardown.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_records_log_statement_for_completion(
        self, mocked_clear_metrics_tables: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given a mocked `AWSClient` object
        When `download_files_and_upload()` is called
        Then the correct log is recorded

        Patches:
            `mocked_clear_metrics_tables`: To remove the
                side effects of having to delete records
                from the database

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
        When `_download_file_ingest_and_teardown()` is called
        Then `download_item()` is called from the client

        Patches:
            `mocked_upload_file_and_remove_local_copy`: To remove
                the side effects of opening & ingesting the file

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME

        # When
        _download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        spy_client.download_item.assert_called_once_with(key=fake_key)

    @mock.patch(f"{MODULE_PATH}._upload_file_and_remove_local_copy")
    def test_delegates_call_to_upload_file_and_remove_local_copy(
        self, spy_upload_file_and_remove_local_copy: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        When `_download_file_ingest_and_teardown()` is called
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
        _download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        downloaded_item_filepath = spy_client.download_item.return_value
        spy_upload_file_and_remove_local_copy.assert_called_once_with(
            filepath=downloaded_item_filepath
        )

    @mock.patch(f"{MODULE_PATH}._upload_file_and_remove_local_copy")
    def test_delegates_call_to_move_file_to_processed_folder(
        self, mocked_upload_file_and_remove_local_copy: mock.MagicMock
    ):
        """
        Given a mocked `AWSClient` object and a fake item key
        When `_download_file_ingest_and_teardown()` is called
        Then `move_file_to_processed_folder()` is called from the client

        Patches:
            `mocked_upload_file_and_remove_local_copy`: To remove
                the side effects of opening & ingesting the file

        """
        # Given
        spy_client = mock.MagicMock()
        fake_key = FAKE_FILENAME

        # When
        _download_file_ingest_and_teardown(key=fake_key, client=spy_client)

        # Then
        spy_client.move_file_to_processed_folder.assert_called_once_with(key=fake_key)


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
