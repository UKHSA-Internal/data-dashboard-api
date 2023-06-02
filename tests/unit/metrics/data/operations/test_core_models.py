from unittest import TestCase, mock

import pandas as pd

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


class TestCheckFile(TestCase):
    def test_file_does_not_exist(self):
        self.assertRaises(FileNotFoundError, check_file, "/doesnotexist")

    def test_column_missing(self):
        self.assertRaises(ValueError, check_file, filename=bad_file)

    def test_file_has_required_fields(self):
        incoming_df = check_file(filename=good_file)
        pd.testing.assert_frame_equal(mock_df, incoming_df)


class TestMaintainModels(TestCase):
    manager = Theme.objects
    existing_model = mock.Mock(spec=manager)
    existing_model.all.return_value.values.return_value = [
        {"pk": 1, "name": "infectious_disease"}
    ]

    def test_no_new_new_model_values(self):
        input_df = mock_df[0:2]  # infectious_disease * 2

        output_df: pd.DataFrame = maintain_model(
            incoming_df=input_df,
            fields={"parent_theme": "name"},
            model=self.existing_model,
        )

        # Function should have merely replaced the column with pk values
        input_df = input_df.replace(to_replace="infectious_disease", value=1)

        pd.testing.assert_frame_equal(
            input_df.reset_index(drop=True),
            output_df.reset_index(drop=True),
            check_like=True,
        )
        self.existing_model.create.assert_not_called()
        self.existing_model.reset_mock()

    def test_model_adds_new_pks(self, mock_model=None):
        input_df = mock_df[3:5]  # infectious_disease & another_new_infectious_disease

        self.existing_model.create.return_value = mock.Mock(spec=self.manager, pk=123)

        output_df: pd.DataFrame = maintain_model(
            incoming_df=input_df,
            fields={"parent_theme": "name"},
            model=self.existing_model,
        )

        # This is what the function should have achieved
        # So, added a new record to the model
        # and replaced column with pk values
        input_df = input_df.replace(to_replace="infectious_disease", value=1)
        input_df = input_df.replace(
            to_replace="another_new_infectious_disease", value=123
        )

        pd.testing.assert_frame_equal(
            input_df.reset_index(drop=True),
            output_df.reset_index(drop=True),
            check_like=True,
        )
        self.existing_model.reset_mock()


class TestLoadCoreData(TestCase):
    @mock.patch("metrics.data.operations.core_models.maintain_model")
    def test_loader(self, mock_maintain_model):
        mock_maintain_model.return_value = output_df[1:2]

        mock_model_list = [
            mock.Mock(),
            mock.Mock(),
        ]
        mock_model = mock.Mock()
        mock_model.return_value = mock_model_list

        core_time_series_manager = mock.Mock()

        load_core_data(
            filename=good_file,
            core_time_series_manager=core_time_series_manager,
            core_time_series_model=mock_model,
        )

        core_time_series_manager.bulk_create.assert_called_once_with(
            [mock_model_list], ignore_conflicts=True, batch_size=100
        )
