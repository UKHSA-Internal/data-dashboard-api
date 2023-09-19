from pathlib import Path
from unittest import mock

from _pytest.logging import LogCaptureFixture
from pydantic_core._pydantic_core import ValidationError

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    CoreTimeSeries,
    Geography,
    GeographyType,
    Metric,
    MetricGroup,
    Stratum,
    SubTheme,
    Theme,
    Topic,
)
from metrics.data.operations.truncated_dataset import (
    _gather_test_data_source_file_paths,
    clear_metrics_tables,
    collect_all_metric_models,
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
        assert len(gathered_test_file_paths) == 52


class TestCollectAllMetricModels:
    def test_delegates_call_for_each_model(self):
        """
        Given no input
        When `collect_all_metric_models()` is called
        Then the correct metric models are returned
        """
        # Given / When
        metric_models = collect_all_metric_models()

        # Then
        assert CoreHeadline in metric_models
        assert CoreTimeSeries in metric_models
        assert APITimeSeries in metric_models
        assert Theme in metric_models
        assert SubTheme in metric_models
        assert Topic in metric_models
        assert MetricGroup in metric_models
        assert Metric in metric_models
        assert GeographyType in metric_models
        assert Geography in metric_models
        assert Stratum in metric_models
        assert Age in metric_models


class TestClearMetricsTables:
    @mock.patch(f"{MODULE_PATH}.collect_all_metric_models")
    def test_calls_delete_on_collected_models(
        self, spy_collect_all_metric_models: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given no input
        When `clear_metrics_tables()` is called
        Then `objects.all().delete()` is called
            on each of the models returned from `collect_all_metric_models()`

        Patches:
            `spy_collect_all_metric_models`: To isolate the
                returned models and cast the main assertions on them

        """
        # Given
        mocked_collected_metric_models = [
            mock.MagicMock(__name__=f"model-{i}") for i in range(10)
        ]
        spy_collect_all_metric_models.return_value = mocked_collected_metric_models

        # When
        clear_metrics_tables()

        # Then
        for mocked_metric_model in mocked_collected_metric_models:
            assert mock.call.objects.all().delete() in mocked_metric_model.mock_calls

    @mock.patch(f"{MODULE_PATH}.collect_all_metric_models")
    def test_records_expected_logs(
        self, spy_collect_all_metric_models: mock.MagicMock, caplog: LogCaptureFixture
    ):
        """
        Given no input
        When `clear_metrics_tables()` is called
        Then the correct logs are recorded

        Patches:
            `spy_collect_all_metric_models`: To isolate the
                returned models

        """
        # Given
        mocked_collected_metric_models = [
            mock.MagicMock(__name__=f"model-{i}") for i in range(10)
        ]
        # `MagicMock` does not implement `__name__` by default hence the need to explicitly set it here
        spy_collect_all_metric_models.return_value = mocked_collected_metric_models

        # When
        clear_metrics_tables()

        # Then
        for mocked_metric_model in mocked_collected_metric_models:
            assert f"Deleting records of {mocked_metric_model.__name__}" in caplog.text

        assert "Completed deleting existing metrics records" in caplog.text


class TestUploadTruncatedTestData:
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_error_log_made_for_failed_file(
        self,
        mocked_file_ingester: mock.MagicMock,
        mocked_clear_metrics_tables: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given the `file_ingester()` which will fail
        When `upload_truncated_test_data()` is called
        Then the correct log is made

        Patches:
            `mocked_file_ingester`: To simulate an error
                occuring when uploading a file via the
                call to the `file_ingester()` function
            `mocked_clear_metrics_tables`: To remove
                the side effect of clearing records
                and having to hit the database
        """
        # Given
        mocked_file_ingester.side_effect = ValidationError

        # When
        upload_truncated_test_data()

        # Then
        assert "Failed upload of" in caplog.text

    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_logs_made_correctly(
        self,
        mocked_file_ingester: mock.MagicMock,
        mocked_clear_metrics_tables: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given a set of truncated test files
        When `upload_truncated_test_data()` is called
        Then `file_ingester()` is called for each file

        Patches:
            `mocked_file_ingester`: To remove side effects
                of having to upload to the database
            `mocked_clear_metrics_tables`: To remove
                the side effect of clearing records
                and having to hit the database
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

    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    @mock.patch(f"{MODULE_PATH}.file_ingester")
    def test_delegates_calls_successfully_for_each_source_file(
        self,
        spy_file_ingester: mock.MagicMock,
        mocked_clear_metrics_tables: mock.MagicMock,
    ):
        """
        Given a set of truncated test files
        When `upload_truncated_test_data()` is called
        Then `file_ingester()` is called for each file

        Patches:
            `spy_file_ingester`: For the main assertion
                 and for collecting the calls which were made
            `mocked_clear_metrics_tables`: To remove
                the side effect of clearing records
                and having to hit the database
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

    @mock.patch(f"{MODULE_PATH}.file_ingester")
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_delegates_call_to_delete_existing_metrics(
        self,
        spy_clear_metrics_tables: mock.MagicMock,
        mocked_file_ingester: mock.MagicMock,
    ):
        """
        Given no input
        When `upload_truncated_test_data()` is called
        Then `clear_metrics_tables()` is called to clear
            the existing records in the metrics tables

        Patches:
            `spy_clear_metrics_tables`: For the main assertion
            `mocked_file_ingester`: To remove side effects
                of having to upload to the database
        """
        # Given / When
        upload_truncated_test_data()

        # Then
        spy_clear_metrics_tables.assert_called_once()
