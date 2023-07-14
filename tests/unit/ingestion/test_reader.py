from unittest import mock

import pandas as pd
import pytest

from ingestion.consumer import Reader
from ingestion.reader import COLUMN_NAMES_WITH_FOREIGN_KEYS
from metrics.data.enums import TimePeriod

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
    @mock.patch.object(Reader, "_cast_sex_column_to_expected_values")
    def test_parse_dataframe_as_iterable_calls_method_to_cast_sex_column(
        self,
        spy_cast_sex_column_to_expected_values: mock.MagicMock,
        spy_cast_int_type_on_columns_with_foreign_keys: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_cast_sex_column_to_expected_values()` method

        Patches:
            `spy_cast_sex_column_to_expected_values`: For
                the main assertion
            `spy_cast_int_type_on_columns_with_foreign_keys`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_cast_sex_column_to_expected_values()`

        """
        # Given
        mocked_dataframe = mock.MagicMock()
        reader = Reader(data=mock.Mock())

        # When
        reader.parse_dataframe_as_iterable(dataframe=mocked_dataframe)

        # Then
        dataframe_from_previous_callee_method = (
            spy_cast_int_type_on_columns_with_foreign_keys.return_value
        )
        spy_cast_sex_column_to_expected_values.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch.object(Reader, "_cast_sex_column_to_expected_values")
    @mock.patch.object(Reader, "_create_named_tuple_iterable")
    def test_parse_dataframe_as_iterable_calls_method_to_create_iterable(
        self,
        spy_create_named_tuple_iterable: mock.MagicMock,
        spy_cast_sex_column_to_expected_values: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `parse_dataframe_as_iterable()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_create_named_tuple_iterable()` method

        Patches:
            `spy_create_named_tuple_iterable`: For
                the main assertion
            `spy_cast_sex_column_to_expected_values`: To isolate
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
            spy_cast_sex_column_to_expected_values.return_value
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
            `_create_named_tuple_iterable()` method for the return value

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

    def test_cast_int_type_on_columns_with_foreign_keys(self):
        """
        Given a `DataFrame` which contains IDs as floats
            for the supporting model columns
        When `_cast_int_type_on_columns_with_foreign_keys()` is called
            from an instance of `Reader`
        Then the supporting model columns i.e. those with foreign keys
            will all be cast to int types
        """
        # Given
        record = {
            "parent_theme": 1.00,
            "child_theme": 1.0,
            "topic": 1.000,
            "geography": 2,
            "geography_type": 1,
            "metric_group": 3,
            "metric": 4.0,
            "stratum": 1,
            "age": 1.0000,
        }
        data = [record]
        dataframe = pd.DataFrame(data)
        reader = Reader(data=data)

        # When
        returned_dataframe = reader._cast_int_type_on_columns_with_foreign_keys(
            dataframe=dataframe
        )

        # Then
        for column_name, value in record.items():
            assert getattr(returned_dataframe, column_name)[0] == int(value)

    @pytest.mark.parametrize("column_name_to_remove", COLUMN_NAMES_WITH_FOREIGN_KEYS)
    def test_cast_int_type_on_columns_with_foreign_keys_raises_error(
        self, column_name_to_remove: str
    ):
        """
        Given a `DataFrame` which does not contain all the required columns
        When `_cast_int_type_on_columns_with_foreign_keys()`
            is called from an instance of `Reader`
        Then a `KeyError` is raised
        """
        # Given
        record = {
            "parent_theme": 1.00,
            "child_theme": 1.0,
            "topic": 1.000,
            "geography": 2,
            "geography_type": 1,
            "metric_group": 3,
            "metric": 4.0,
            "stratum": 1,
            "age": 1.0000,
        }
        record.pop(column_name_to_remove)
        data = [record]
        dataframe = pd.DataFrame(data)
        reader = Reader(data=data)

        # When
        with pytest.raises(KeyError):
            reader._cast_int_type_on_columns_with_foreign_keys(dataframe=dataframe)

    def test_remove_rows_with_nan_metric_value(self):
        """
        Given a `DataFrame` which contains "metric_value" column values of NaN
        When `_remove_rows_with_nan_metric_value()`
            is called from an instance of `Reader`
        Then the rows which contain NaN values are removed
        """
        # Given
        data = [
            {"metric_value": None, "topic": "Influenza"},
            {"metric_value": 123, "topic": "RSV"},
        ]
        dataframe = pd.DataFrame(data)
        assert len(dataframe) == 2
        reader = Reader(data=data)

        # When
        returned_dataframe = reader._remove_rows_with_nan_metric_value(
            dataframe=dataframe
        )

        # Then
        assert len(returned_dataframe) == 1
        assert returned_dataframe.metric_value.item() == 123

    def test_remove_rows_with_nan_metric_value_does_not_remove_valid_rows(self):
        """
        Given a `DataFrame` which does not contain
            any "metric_value" column values of NaN
        When `_remove_rows_with_nan_metric_value()`
            is called from an instance of `Reader`
        Then the original dataframe is returned
        """
        # Given
        data = [
            {"metric_value": 123, "topic": "Influenza"},
            {"metric_value": 123, "topic": "RSV"},
        ]
        original_dataframe = pd.DataFrame(data)
        assert len(original_dataframe) == 2
        reader = Reader(data=data)

        # When
        returned_dataframe = reader._remove_rows_with_nan_metric_value(
            dataframe=original_dataframe
        )

        # Then
        assert len(returned_dataframe) == 2
        assert returned_dataframe.equals(original_dataframe)

    def test_concatenate_new_records(self):
        """
        Given a `DataFrame` and a list of data of new records
        When `_concatenate_new_records()`
            is called from an instance of `Reader`
        Then the returned dataframe contains
           the original dataframe contents and the new records
        """
        # Given
        data = [
            {"metric_value": 123, "topic": "Influenza"},
            {"metric_value": 456, "topic": "RSV"},
        ]
        original_dataframe = pd.DataFrame(data)
        new_records_data = [
            {"metric_value": 789, "topic": "Parainfluenza"},
        ]
        reader = Reader(data=data)

        # When
        returned_dataframe: pd.DataFrame = reader._concatenate_new_records(
            dataframe=original_dataframe, new_records_data=new_records_data
        )

        # Then
        assert len(returned_dataframe) == 3

        values = returned_dataframe.values
        assert values[0][0] == data[0]["metric_value"]
        assert values[0][1] == data[0]["topic"]

        assert values[1][0] == data[1]["metric_value"]
        assert values[1][1] == data[1]["topic"]

        assert values[2][0] == new_records_data[0]["metric_value"]
        assert values[2][1] == new_records_data[0]["topic"]

    def test_drop_text_representation_of_columns(self):
        """
        Given a `DataFrame` and a dict of fields to be removed
        When `_drop_text_representations_of_columns()`
            is called from an instance of `Reader`
        Then the returned dataframe does not contain
            the columns required to be dropped by the given `fields`
        """
        # Given
        data = [
            {
                "parent_theme": "infectious_disease",
                "child_theme": "respiratory",
                "name": "infectious_disease",
            }
        ]
        dataframe = pd.DataFrame(data=data)
        fields = {"parent_theme": "name"}
        reader = Reader(data=data)

        # When
        returned_dataframe = reader._drop_text_representations_of_columns(
            dataframe=dataframe, fields=fields
        )

        # Then
        # Check the columns matching the given `fields` are dropped
        assert "parent_theme" not in returned_dataframe.columns
        assert "name" not in returned_dataframe.columns

        # Check other columns remain in the returned dataframe
        assert "child_theme" in returned_dataframe.columns

    def test_rename_columns_to_original_names(self):
        """
        Given a `DataFrame` containing a "pk" column
        When `_rename_columns_to_original_names()`
            is called from an instance of `Reader`
        Then the "pk" column is replaced with the "parent_theme"
            column according to the given `fields`
        """
        # Given
        data = [
            {
                "pk": 1,
                "child_theme": "respiratory",
                "name": "infectious_disease",
            }
        ]
        dataframe = pd.DataFrame(data=data)
        fields = {"parent_theme": "name"}
        reader = Reader(data=data)

        # When
        returned_dataframe = reader._rename_columns_to_original_names(
            dataframe=dataframe, fields=fields
        )

        # Then
        assert "parent_theme" in returned_dataframe.columns
        assert "pk" not in returned_dataframe.columns

        record = next(returned_dataframe.itertuples())
        assert record.parent_theme == 1

    def test_merge_left_join(self):
        """
        Given a `DataFrame` and another dataframe to be merged in
        When `_merge_left_join()` is called from an instance of `Reader`
        Then the returned dataframe contains the merged contents
        """
        # Given
        incoming_data = pd.DataFrame([{"parent_theme": "infectious_disease"}])
        existing_data = pd.DataFrame([{"name": None}])
        reader = Reader(data=mock.Mock())

        # When
        returned_dataframe = reader._merge_left_join(
            left_data=incoming_data,
            right_data=existing_data,
            fields={"parent_theme": "name"},
        )

        # Then
        assert "name" in returned_dataframe.columns
        assert "parent_theme" in returned_dataframe.columns

        record = next(returned_dataframe.itertuples())
        assert record.parent_theme == "infectious_disease"
        assert record[3] == "left_only"

    def test_get_new_data_in_source(self):
        """
        Given a `DataFrame` which has undergone a left join merge
        When `_get_new_data_in_source()` is called from
            an instance of `Reader`
        Then the returned dict contains the expected values
        """
        # Given
        dataframe = pd.DataFrame(
            [
                {
                    "parent_theme": "infectious_disease",
                    "name": None,
                    "_merge": "left_only",
                }
            ]
        )
        fields = {"parent_theme": "name"}
        reader = Reader(data=mock.Mock())

        # When
        returned_data: list[dict[str, str]] = reader._get_new_data_in_source(
            dataframe=dataframe, fields=fields
        )

        # Then
        assert returned_data[0]["name"] == "infectious_disease"

    def test_merge_inner(self):
        """
        Given a `DataFrame` and another dataframe to be merged in
        When `_merge_inner()` is called from an instance of `Reader`
        Then the returned dataframe contains the merged contents
        """
        # Given
        incoming_data = pd.DataFrame([{"parent_theme": "infectious_disease"}])
        data_to_add = pd.DataFrame([{"name": "infectious_disease", "pk": 1}])
        reader = Reader(data=mock.Mock())

        # When
        returned_dataframe = reader._merge_inner(
            left_data=incoming_data,
            right_data=data_to_add,
            fields={"parent_theme": "name"},
        )

        # Then
        record = next(returned_dataframe.itertuples())
        assert record.parent_theme == record.name == "infectious_disease"
        assert record.pk == 1

    def test_create_new_records_data(self):
        """
        Given a list of data required to create new records
        When `_create_new_records_data()`
            is called from an instance of `Reader`
        Then a list of data is returned, including the
            pk of the new record created via the model manager
        """
        # Given
        spy_model_manager = mock.Mock()
        new_data_for_records = [{"parent_theme": "infectious_disease"}]
        reader = Reader(data=mock.Mock())

        # When
        new_records_data: list[dict[str, str]] = reader._create_new_records_data(
            new_data=new_data_for_records, model_manager=spy_model_manager
        )

        # Then
        expected_record_pk = spy_model_manager.create.return_value.pk
        expected_created_record_data = {
            "parent_theme": "infectious_disease",
            "pk": expected_record_pk,
        }
        assert new_records_data == [expected_created_record_data]

    def test_get_existing_records_for_values_returns_dataframe_for_existing_records(
        self,
    ):
        """
        Given a model manager which contain an existing record
        When `_get_existing_records_for_values()` is called
            from an instance of `Reader`
        Then a dataframe is returned with the data for
            any matching existing records
        """
        # Given
        mocked_model_manager = mock.MagicMock()
        mocked_model_manager.all.return_value.values.return_value = [
            {"parent_theme": "infectious_disease", "pk": 123},
        ]
        fields = {"parent_theme": "name"}
        reader = Reader(data=mock.Mock())

        # When
        returned_dataframe = reader._get_existing_records_for_values(
            fields=fields, model_manager=mocked_model_manager
        )

        # Then
        record = next(returned_dataframe.itertuples())
        assert record.parent_theme == "infectious_disease"
        assert record.pk == 123

    def test_get_existing_records_for_values_returns_empty_dataframe_for_no_records(
        self,
    ):
        """
        Given a model manager which does not contain any records
        When `_get_existing_records_for_values()` is called
            from an instance of `Reader`
        Then an empty dataframe is returned with the
            fields values as column names
        """
        # Given
        mocked_model_manager = mock.MagicMock()
        mocked_model_manager.all.return_value.values.return_value = []
        fields = {"parent_theme": "name"}
        reader = Reader(data=mock.Mock())

        # When
        returned_dataframe = reader._get_existing_records_for_values(
            fields=fields, model_manager=mocked_model_manager
        )

        # Then
        assert returned_dataframe.empty

    @pytest.mark.parametrize(
        "sex_column_value, expected_value",
        (
            ["all", "ALL"],
            ["female", "F"],
            ["male", "M"],
        ),
    )
    def test_cast_sex_column_to_expected_values(
        self, sex_column_value: str, expected_value: str
    ):
        """
        Given a `DataFrame` which contains a "sex" column
        When `_cast_sex_column_to_expected_values()`
            is called from an instance of `Reader`
        Then the returned dataframe has cast the "sex" column
            to a set of expected values
        """
        # Given
        dataframe = pd.DataFrame([{"sex": sex_column_value}])
        reader = Reader(data=mock.Mock())

        # When
        returned_dataframe = reader._cast_sex_column_to_expected_values(
            dataframe=dataframe,
        )

        # Then
        iterable = returned_dataframe.itertuples()
        record = next(iterable)
        assert record.sex == expected_value

    @pytest.mark.parametrize(
        "metric_frequency_column_value, expected_value",
        (
            ["daily", TimePeriod.Daily.value],
            ["weekly", TimePeriod.Weekly.value],
            ["monthly", TimePeriod.Monthly.value],
            ["quarterly", TimePeriod.Quarterly.value],
            ["annual", TimePeriod.Annual.value],
        ),
    )
    def test_cast_metric_frequency_column_to_expected_values(
        self, metric_frequency_column_value: str, expected_value: str
    ):
        """
        Given a `DataFrame` which contains a "metric_frequency" column
        When `_cast_metric_frequency_column_to_expected_values()`
            is called from an instance of `Reader`
        Then the returned dataframe has cast the "metric_frequency" column
            to a set of expected values
        """
        # Given
        dataframe = pd.DataFrame([{"metric_frequency": metric_frequency_column_value}])
        reader = Reader(data=mock.Mock())

        # When
        returned_dataframe = reader._cast_metric_frequency_column_to_expected_values(
            dataframe=dataframe,
        )

        # Then
        iterable = returned_dataframe.itertuples()
        record = next(iterable)
        assert record.metric_frequency == expected_value
