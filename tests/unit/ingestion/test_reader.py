from unittest import mock

import pandas as pd

from ingestion.consumer import Reader
from ingestion.reader import COLUMN_NAMES_WITH_FOREIGN_KEYS

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
    @mock.patch.object(Reader, "_create_named_tuple_iterable")
    def test_parse_dataframe_as_iterable_calls_method_to_create_iterable(
        self,
        spy_create_named_tuple_iterable: mock.MagicMock,
        spy_cast_int_type_on_columns_with_foreign_keys: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_cast_int_type_on_columns_with_foreign_keys()` method

        Patches:
            `spy_create_named_tuple_iterable`: For
                the main assertion
            `spy_cast_int_type_on_columns_with_foreign_keys`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_create_named_tuple_iterable()`

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
        spy_create_named_tuple_iterable.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch.object(Reader, "_create_named_tuple_iterable")
    def test_parse_dataframe_as_iterable_calls_method_for_return_value(
        self,
        spy_create_named_tuple_iterable: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then the final call is delegated to the
            `spy_create_named_tuple_iterable()` method

        Patches:
            `spy_create_named_tuple_iterable`: For
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
        assert returned_iterable == spy_create_named_tuple_iterable.return_value

    def test_get_unique_values_from_dataframe_for_keys_for_single_key(self):
        """
        Given a `DataFrame` which contains multiple rows
            with duplicate values for a specific field
        When `_get_unique_values_from_dataframe_for_keys()` is called
            from an instance of `Reader`
        Then the returned dataframe does not contain duplicate values
        """
        # Given
        theme = "infectious_disease"
        data = [
            {"parent_theme": theme, "topic": "Influenza"},
            {"parent_theme": theme, "topic": "RSV"},
        ]
        dataframe = pd.DataFrame(data)
        assert len(dataframe) == 2

        fields = {"parent_theme": "name"}
        reader = Reader(data=data)

        # When
        deduplicated_dataframe: pd.DataFrame = (
            reader._get_unique_values_from_dataframe_for_keys(
                dataframe=dataframe, fields=fields
            )
        )

        # Then
        # In this case, the "parent_theme" key was requested
        # So this column is the focus of the new dataframe
        # And is consequently deduplicated
        assert len(deduplicated_dataframe) == 1
        assert deduplicated_dataframe.values.all() == theme

    def test_create_named_tuple_iterable(self):
        """
        Given a `DataFrame` which contains dummy data
        When `_create_named_tuple_iterable()` is called
            from an instance of `Reader`
        Then an iterable of named tuples for each data row is returned
        """
        # Given
        theme_name = "infectious_disease"
        topic_name = "Influenza"
        data = [
            {"parent_theme": theme_name, "topic": topic_name},
        ]
        dataframe = pd.DataFrame(data)
        reader = Reader(data=data)

        # When
        named_tuple_iterable = reader._create_named_tuple_iterable(dataframe=dataframe)

        # Then
        named_tuple = next(named_tuple_iterable)
        assert named_tuple.parent_theme == "infectious_disease"
        assert named_tuple.topic == topic_name

