from pathlib import Path
from unittest import mock

from _pytest.logging import LogCaptureFixture
from pydantic_core._pydantic_core import ValidationError

from metrics.data.operations.truncated_dataset import (
    _gather_test_data_source_file_paths,
    upload_truncated_test_data,
)

MODULE_PATH = "metrics.data.operations.truncated_dataset"


class TestGatherTestDataSourceFilePaths:
    def test_returns_correct_list_of_files(self):
        """
        Given no input files
        When `_gather_test_data_source_file_paths()`
        Then the correct list of file paths is returned
        """
        # Given / When
        gathered_test_file_paths: list[Path] = _gather_test_data_source_file_paths()

        # Then
        assert len(gathered_test_file_paths) == 53


class TestUploadTruncatedTestData:
    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_error_log_made_for_failed_file(
        self, mocked_file_ingester: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given the `file_ingester()` which will fail
        When `upload_truncated_test_data()` is called
        Then the correct log is made

        Patches:
            `mocked_file_ingester`: To simulate an error
                occuring when uploading a file via the
                call to the `file_ingester()` function
        """
        # Given
        mocked_file_ingester.side_effect = ValidationError

        # When
        upload_truncated_test_data()

        # Then
        assert "Failed upload of" in caplog.text

    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_logs_made_correctly(
        self, mocked_file_ingester: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given a set of truncated test files
        When `upload_truncated_test_data()` is called
        Then `file_ingester()` is called for each file

        Patches:
            `mocked_file_ingester`: To remove side effects
                of having to upload to the database
        """
        # Given
        gathered_test_file_paths: list[Path] = _gather_test_data_source_file_paths()

        # When
        upload_truncated_test_data()

        # Then
        formatted_logged_text: str = caplog.text
        for gathered_test_file_path in gathered_test_file_paths:
            gathered_test_file_name = gathered_test_file_path.name

            assert f"Uploading {gathered_test_file_name}" in formatted_logged_text
            assert f"Completed {gathered_test_file_name}" in formatted_logged_text

        assert "Completed truncated dataset upload" in formatted_logged_text

    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_delegates_calls_successfully_for_each_source_file(
        self, spy_file_ingester: mock.MagicMock
    ):
        """
        Given a set of truncated test files
        When `upload_truncated_test_data()` is called
        Then `file_ingester()` is called for each file

        Patches:
            `spy_file_ingester`: For the main assertion
                 and for collecting the calls which were made
        """
        # Given
        gathered_test_file_paths: list[Path] = _gather_test_data_source_file_paths()

        # When
        upload_truncated_test_data()

        # Then
        file_paths_called_by_file_ingester = []
        # Get the names of all the files which were opened and given to the `file_ingester()`
        for mock_call_made in spy_file_ingester.mock_calls:
            call_kwargs = mock_call_made.kwargs
            # There will be a few magic method calls that we don't want to include
            # hence the filtering for calls made specifically with a file
            if "file" in call_kwargs:
                file_paths_called_by_file_ingester.append(call_kwargs["file"].name)

        # Check that they match with the gathered test file paths
        for gathered_test_file_path in gathered_test_file_paths:
            assert str(gathered_test_file_path) in file_paths_called_by_file_ingester
