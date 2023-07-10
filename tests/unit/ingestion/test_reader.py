from typing import Type
from unittest import mock

import pytest
from django.db.models.manager import Manager

from ingestion.consumer import FieldsAndModelManager, HeadlineDTO, Ingestion, Reader
from ingestion.reader import COLUMN_NAMES_WITH_FOREIGN_KEYS
from metrics.data.models import core_models

MODULE_PATH = "ingestion.reader"


class TestReader:
    def test_supporting_model_column_names(self):
        """
        Given mocked data
        When the `supporting_model_column_names` property
            is called from an instance of `Reader`
        Then the correct list of strings is returned
        """
        # Given
        mocked_data = mock.Mock()
        reader = Reader(data=mocked_data)

        # When
        returned_column_names: tuple[str, ...] = reader.supporting_model_column_names

        # Then
        assert returned_column_names == COLUMN_NAMES_WITH_FOREIGN_KEYS

    @mock.patch(f"{MODULE_PATH}.pd")
    def test_open_data_as_dataframe(self, spy_pandas: mock.MagicMock):
        """
        Given mocked data
        When `open_data_as_dataframe()` is called
            from an instance of `Reader`
        Then the call is delegated to `read_json()`
            from the `pandas` library

        Patches:
            `spy_pd`: For the main assertion of
                checking the contract with `read_json()`
                from the `pandas` library
        """
        # Given
        mocked_data = mock.Mock()
        reader = Reader(data=mocked_data)

        # When
        returned_dataframe = reader.open_data_as_dataframe()

        # Then
        spy_pandas.read_json.assert_called_once_with(mocked_data)
        assert returned_dataframe == spy_pandas.read_json.return_value

    # Tests for `parse_dataframe_as_iterable()`

    @mock.patch.object(Reader, "_remove_rows_with_nan_metric_value")
    def test_parse_dataframe_as_iterable_calls_method_to_remove_nan_rows(
        self,
        spy_remove_rows_with_nan_metric_value: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_remove_rows_with_nan_metric_value()` method

        Patches:
            `spy_remove_rows_with_nan_metric_value`: For the
                main assertion
        """
        # Given
        mocked_dataframe = mock.Mock()
        reader = Reader(data=mock.Mock())

        # When
        reader.parse_dataframe_as_iterable(dataframe=mocked_dataframe)

        # Then
        spy_remove_rows_with_nan_metric_value.assert_called_once_with(
            dataframe=mocked_dataframe
        )

    @mock.patch.object(Reader, "_remove_rows_with_nan_metric_value")
    @mock.patch.object(Reader, "_cast_int_type_on_columns_with_foreign_keys")
    def test_parse_dataframe_as_iterable_calls_method_to_cast_int_type_to_columns(
        self,
        spy_cast_int_type_on_columns_with_foreign_keys: mock.MagicMock,
        spy_remove_rows_with_nan_metric_value: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_cast_int_type_on_columns_with_foreign_keys()` method

        Patches:
            `spy_cast_int_type_on_columns_with_foreign_keys`: For
                the main assertion
            `spy_remove_rows_with_nan_metric_value`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_cast_int_type_on_columns_with_foreign_keys()`

        """
        # Given
        mocked_dataframe = mock.Mock()
        reader = Reader(data=mock.Mock())

        # When
        reader.parse_dataframe_as_iterable(dataframe=mocked_dataframe)

        # Then
        dataframe_from_previous_callee_method = (
            spy_remove_rows_with_nan_metric_value.return_value
        )
        spy_cast_int_type_on_columns_with_foreign_keys.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch.object(Reader, "_cast_int_type_on_columns_with_foreign_keys")
    @mock.patch.object(Reader, "_create_named_tuple_iterable_from")
    def test_parse_dataframe_as_iterable_calls_method_to_create_iterable(
        self,
        spy_create_named_tuple_iterable_from: mock.MagicMock,
        spy_cast_int_type_on_columns_with_foreign_keys: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_cast_int_type_on_columns_with_foreign_keys()` method

        Patches:
            `spy_create_named_tuple_iterable_from`: For
                the main assertion
            `spy_cast_int_type_on_columns_with_foreign_keys`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_create_named_tuple_iterable_from()`

        """
        # Given
        mocked_dataframe = mock.MagicMock()
        ingestion = Reader(data=mock.Mock())

        # When
        ingestion.parse_dataframe_as_iterable(dataframe=mocked_dataframe)

        # Then
        dataframe_from_previous_callee_method = (
            spy_cast_int_type_on_columns_with_foreign_keys.return_value
        )
        spy_create_named_tuple_iterable_from.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch.object(Reader, "_create_named_tuple_iterable_from")
    def test_parse_dataframe_as_iterable_calls_method_for_return_value(
        self,
        spy_create_named_tuple_iterable_from: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then the final call is delegated to the
            `spy_create_named_tuple_iterable_from()` method

        Patches:
            `spy_create_named_tuple_iterable_from`: For
                the main assertion

        """
        # Given
        mocked_dataframe = mock.MagicMock()
        reader = Reader(data=mock.Mock())

        # When
        returned_iterable = reader.parse_dataframe_as_iterable(
            dataframe=mocked_dataframe
        )

        # Then
        assert returned_iterable == spy_create_named_tuple_iterable_from.return_value

    @pytest.mark.parametrize(
        "expected_index, expected_fields, expected_model_manager_from_class",
        [
            (0, {"parent_theme": "name"}, "theme_manager"),
            (
                1,
                {"child_theme": "name", "parent_theme": "theme_id"},
                "sub_theme_manager",
            ),
            (2, {"topic": "name", "child_theme": "sub_theme_id"}, "topic_manager"),
            (3, {"geography_type": "name"}, "geography_type_manager"),
            (
                4,
                {"geography": "name", "geography_type": "geography_type_id"},
                "geography_manager",
            ),
            (5, {"metric_group": "name", "topic": "topic_id"}, "metric_group_manager"),
            (
                6,
                {
                    "metric": "name",
                    "metric_group": "metric_group_id",
                    "topic": "topic_id",
                },
                "metric_manager",
            ),
            (7, {"stratum": "name"}, "stratum_manager"),
            (8, {"age": "name"}, "age_manager"),
        ],
    )
    def test_get_all_related_fields_and_model_managers(
        self,
        expected_index: int,
        expected_fields: dict[str, str],
        expected_model_manager_from_class: str,
    ):
        """
        Given mocked data
        When `get_all_related_fields_and_model_managers()` is called
            from an instance of `Ingestion`
        Then the correct list of named tuples is returned
            where each named tuple contains the
            relevant fields and the corresponding model manager
        """
        # Given
        mocked_data = mock.Mock()
        ingestion = Ingestion(data=mocked_data)

        # When
        all_related_fields_and_model_managers: list[
            FieldsAndModelManager
        ] = ingestion.get_all_related_fields_and_model_managers()

        # Then
        assert (
            all_related_fields_and_model_managers[expected_index].fields
            == expected_fields
        )
        assert all_related_fields_and_model_managers[
            expected_index
        ].model_manager == getattr(ingestion, expected_model_manager_from_class)
