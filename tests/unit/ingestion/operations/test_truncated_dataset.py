from pathlib import Path
from unittest import mock

from _pytest.logging import LogCaptureFixture

from ingestion.operations.truncated_dataset import (
    _gather_test_data_source_file_paths,
    clear_metrics_tables,
    collect_all_metric_model_managers,
    upload_truncated_test_data,
)
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

MODULE_PATH = "ingestion.operations.truncated_dataset"


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
        assert len(gathered_test_file_paths) == 1408


class TestCollectAllMetricModelManagers:
    def test_delegates_call_for_each_model(self):
        """
        Given no input
        When `collect_all_metric_model_managers()` is called
        Then the correct metric models are returned
        """
        # Given / When
        metric_models = collect_all_metric_model_managers()

        # Then
        assert CoreHeadline.objects in metric_models
        assert CoreTimeSeries.objects in metric_models
        assert APITimeSeries.objects in metric_models
        assert Theme.objects in metric_models
        assert SubTheme.objects in metric_models
        assert Topic.objects in metric_models
        assert MetricGroup.objects in metric_models
        assert Metric.objects in metric_models
        assert GeographyType.objects in metric_models
        assert Geography.objects in metric_models
        assert Stratum.objects in metric_models
        assert Age.objects in metric_models


class TestClearMetricsTables:
    @mock.patch(f"{MODULE_PATH}.collect_all_metric_model_managers")
    def test_calls_delete_on_collected_models(
        self,
        spy_collect_all_metric_model_managers: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given no input
        When `clear_metrics_tables()` is called
        Then `all().delete()` is called on each of the model managers
            returned from `collect_all_metric_model_managers()`

        Patches:
            `spy_collect_all_metric_model_managers`: To isolate the
                returned models and cast the main assertions on them

        """
        # Given
        mocked_collected_metric_model_managers = [
            mock.MagicMock(model=mock.Mock(__name__=f"model-{i}")) for i in range(10)
        ]
        spy_collect_all_metric_model_managers.return_value = (
            mocked_collected_metric_model_managers
        )

        # When
        clear_metrics_tables()

        # Then
        for mocked_metric_model_manager in mocked_collected_metric_model_managers:
            assert mock.call.all().delete() in mocked_metric_model_manager.mock_calls

    @mock.patch(f"{MODULE_PATH}.collect_all_metric_model_managers")
    def test_records_expected_logs(
        self,
        spy_collect_all_metric_model_managers: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given no input
        When `clear_metrics_tables()` is called
        Then the correct logs are recorded

        Patches:
            `spy_collect_all_metric_model_managers`: To isolate the
                returned models

        """
        # Given
        mocked_collected_metric_model_managers = [
            mock.MagicMock(model=mock.Mock(__name__=f"model-{i}")) for i in range(10)
        ]
        # `MagicMock` does not implement `__name__` by default
        # hence the need to explicitly set it here on the inner model
        spy_collect_all_metric_model_managers.return_value = (
            mocked_collected_metric_model_managers
        )

        # When
        clear_metrics_tables()

        # Then
        for mocked_metric_model_manager in mocked_collected_metric_model_managers:
            assert (
                f"Deleting records of {mocked_metric_model_manager.model.__name__}"
                in caplog.text
            )

        assert "Completed deleting existing metrics records" in caplog.text


class TestUploadTruncatedTestData:
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    @mock.patch(f"{MODULE_PATH}.run_with_multiple_processes")
    def test_logs_made_correctly(
        self,
        mocked_run_with_multiple_processes: mock.MagicMock,
        mocked_clear_metrics_tables: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given no input
        When `upload_truncated_test_data()` is called
        Then the correct log statement is recorded

        Patches:
            `mocked_run_with_multiple_processes`: To remove side effects
                of having to create multiple processes
                and upload to the database
            `mocked_clear_metrics_tables`: To remove
                the side effect of clearing records
                and having to hit the database
        """
        # Given / When
        upload_truncated_test_data()

        # Then
        assert "Completed truncated dataset upload" in caplog.text

    @mock.patch(f"{MODULE_PATH}._upload_data_as_file")
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    @mock.patch(f"{MODULE_PATH}.run_with_multiple_processes")
    def test_delegates_call_to_run_with_multiple_processes(
        self,
        spy_run_with_multiple_processes: mock.MagicMock,
        mocked_clear_metrics_tables: mock.MagicMock,
        spy_upload_data_as_file: mock.MagicMock,
    ):
        """
        Given a list of test source data files paths at the `source_data/` directory
        When `upload_truncated_test_data()` is called
        Then `run_with_multiple_processes()` is called
            with the `_upload_file` callable and the list of files

        Patches:
            `spy_run_with_multiple_processes`: To check the upload callable
                is invoked with multiple processes
            `mocked_clear_metrics_tables`: To remove
                the side effect of clearing records
                and having to hit the database
            `spy_upload_data_as_file`: For the main assertion
        """
        # Given
        test_source_data_file_paths = _gather_test_data_source_file_paths()

        # When
        upload_truncated_test_data()

        # Then
        spy_run_with_multiple_processes.assert_called_once_with(
            upload_function=spy_upload_data_as_file, items=test_source_data_file_paths
        )

    @mock.patch(f"{MODULE_PATH}.run_with_multiple_processes")
    @mock.patch(f"{MODULE_PATH}.clear_metrics_tables")
    def test_delegates_call_to_delete_existing_metrics(
        self,
        spy_clear_metrics_tables: mock.MagicMock,
        mocked_run_with_multiple_processes: mock.MagicMock,
    ):
        """
        Given no input
        When `upload_truncated_test_data()` is called
        Then `clear_metrics_tables()` is called to clear
            the existing records in the metrics tables

        Patches:
            `spy_clear_metrics_tables`: For the main assertion
            `mocked_run_with_multiple_processes`: To remove side effects
                of having to create multiple processes
                and upload to the database
        """
        # Given / When
        upload_truncated_test_data()

        # Then
        spy_clear_metrics_tables.assert_called_once()
