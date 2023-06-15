from unittest import mock

import _pytest
import pandas as pd
import pytest

from metrics.data.models.core_models import Theme
from metrics.data.operations.core_models import (
    check_file,
    load_core_data,
    maintain_model,
)

bad_file = "tests/fixtures/bad_sample_data.csv"
good_file = "tests/fixtures/sample_data.csv"
mock_df = pd.read_csv(good_file)
output_df = pd.read_csv("tests/fixtures/output_data.csv")


class TestCheckFile:
    def test_file_does_not_exist(self):
        """
        Given a file which does not exist
        When `check_file()` is called
        Then a FileNotFoundError exception will be raised
        """

        # Given
        filename = "non_existent_file"

        # When/Then
        with pytest.raises(FileNotFoundError):
            check_file(filename=filename)

    def test_column_missing(self):
        """
        Given an input file which has one or more fields missing
        When `check_file()` is called
        Then a ValueError exception will be raised
        """

        # Given
        filename = bad_file

        # When/Then
        with pytest.raises(ValueError):
            check_file(filename=filename)

    def test_file_has_required_columns(self):
        """
        Given an input file which has the required columns
        When `check_file()` is called
        Then the expected DataFrame will be returned
        """

        # Given
        filename = good_file

        # When
        incoming_df = check_file(filename=filename)

        # Then
        pd.testing.assert_frame_equal(mock_df, incoming_df)


class TestMaintainModel:
    manager = Theme.objects
    existing_model = mock.Mock(spec=manager)
    existing_model.all.return_value.values.return_value = [
        {"pk": 1, "name": "infectious_disease"}
    ]

    def test_no_new_new_model_values(self):
        """
        Given an input DataFrame and a list of fields
        When `maintain_model()` is called
        Then the expected DataFrame will be returned
        """

        # Given
        input_df = mock_df[0:2]  # infectious_disease * 2

        # When
        actual_df: pd.DataFrame = maintain_model(
            incoming_df=input_df,
            fields={"parent_theme": "name"},
            model=self.existing_model,
        )

        # Then
        # Function should have merely replaced the column with pk values
        expected_df = input_df.replace(to_replace="infectious_disease", value=1)

        pd.testing.assert_frame_equal(
            expected_df.reset_index(drop=True),
            actual_df.reset_index(drop=True),
            check_like=True,
        )
        self.existing_model.create.assert_not_called()
        self.existing_model.reset_mock()

    def test_model_adds_new_pks(self, mock_model=None):
        """
        Given an input DataFrame and a list of fields
        When `maintain_model()` is called
        Then the expected DataFrame will be returned
        """

        # Given
        input_df = mock_df[3:5]  # infectious_disease & another_new_infectious_disease
        self.existing_model.create.return_value = mock.Mock(spec=self.manager, pk=123)

        # When
        actual_df: pd.DataFrame = maintain_model(
            incoming_df=input_df,
            fields={"parent_theme": "name"},
            model=self.existing_model,
        )

        # This is what the function should have achieved
        # So, added a new record to the model
        # and replaced column with pk values
        expected_df = input_df.replace(to_replace="infectious_disease", value=1)
        expected_df = expected_df.replace(
            to_replace="another_new_infectious_disease", value=123
        )

        # Then
        pd.testing.assert_frame_equal(
            expected_df.reset_index(drop=True),
            actual_df.reset_index(drop=True),
            check_like=True,
        )
        self.existing_model.reset_mock()


class TestLoadCoreData:
    @mock.patch("metrics.data.operations.core_models.maintain_model")
    def test_loader(self, mock_maintain_model):
        """
        Given an input file
        When `load_core_data()` is called
        Then the bulk_create function on the core_time_series_manager is called
        """

        # Given
        mock_maintain_model.return_value = output_df[1:2]

        mock_model_list = [
            mock.Mock(),
            mock.Mock(),
        ]
        mock_model = mock.Mock()
        mock_model.return_value = mock_model_list

        core_time_series_manager = mock.Mock()
        core_time_series_manager.exists.return_value = False

        # When
        load_core_data(
            filename=good_file,
            core_time_series_manager=core_time_series_manager,
            core_time_series_model=mock_model,
        )

        # Then
        core_time_series_manager.bulk_create.assert_called_once_with(
            [mock_model_list], ignore_conflicts=True, batch_size=100
        )


class TestLoadCoreDataFunction:
    def test_returns_early_when_core_time_series_has_existing_records(self):
        """
        Given a `CoreTimeSeriesManager` which returns True when `exists()` is called
        When `load_core_data()` is called
        Then the `bulk_create()` method from the `CoreTimeSeriesManager` is not called
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        spy_core_time_series_manager.exists.return_value = True

        # When
        load_core_data(
            filename=good_file,
            core_time_series_manager=spy_core_time_series_manager,
        )

        # Then
        spy_core_time_series_manager.bulk_create.assert_not_called()

    def test_log_statement_recorded_when_returning_early(
        self, caplog: _pytest.logging.LogCaptureFixture
    ):
        """
        Given `CoreTimeSeriesManager` which returns True when `exists()` is called
        When `load_core_data()` is called
        Then the expected log statement is recorded
        """
        # Given
        mocked_core_time_series_manager = mock.Mock()
        mocked_core_time_series_manager.exists.return_value = True

        # When
        load_core_data(
            filename=mock.Mock(),  # Stubbed
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # Then
        assert "Core Time Series table has existing records" in caplog.text
