from typing import Type
from unittest import mock

import pytest
from django.db.models.manager import Manager

from metrics.data.models import core_models
from metrics.data.operations.ingestion import (
    COLUMN_NAMES_WITH_FOREIGN_KEYS,
    FieldsAndModelManager,
    HeadlineDTO,
    Ingestion,
)

MODULE_PATH = "metrics.data.operations.ingestion"


class TestIngestion:
    def test_to_model(self, example_headline_data_json: list[dict[str, float]]):
        """
        Given a single headline record as a dictionary
        When `to_model()` is called from an instance of `Ingestion`
        Then the returned model is enriched with the correct fields
        """
        # Given
        data = example_headline_data_json[0]
        headline_data = mock.Mock(
            parent_theme=data["parent_theme"],
            child_theme=data["child_theme"],
            metric_group=data["metric_group"],
            topic=data["topic"],
            metric=data["metric"],
            geography_type=data["geography_type"],
            geography=data["geography"],
            age=data["age"],
            sex=data["sex"],
            stratum=data["stratum"],
            period_start=data["period_start"],
            period_end=data["period_end"],
            metric_value=data["metric_value"],
            refresh_date=data["refresh_date"],
        )
        ingestion = Ingestion(data=data)

        # When
        model: HeadlineDTO = ingestion.to_model(data_record=headline_data)

        # Then
        assert model.theme == headline_data.parent_theme == data["parent_theme"]
        assert model.sub_theme == headline_data.child_theme == data["child_theme"]
        assert model.metric_group == headline_data.metric_group == data["metric_group"]
        assert model.topic == headline_data.topic == data["topic"]
        assert model.metric == headline_data.metric == data["metric"]
        assert (
            model.geography_type
            == headline_data.geography_type
            == data["geography_type"]
        )
        assert model.geography == headline_data.geography == data["geography"]
        assert model.age == headline_data.age == data["age"]
        assert model.sex == headline_data.sex == data["sex"]
        assert model.stratum == headline_data.stratum == data["stratum"]
        assert model.period_start == headline_data.period_start == data["period_start"]
        assert model.period_end == headline_data.period_end == data["period_end"]
        assert model.metric_value == headline_data.metric_value == data["metric_value"]
        assert model.refresh_date == headline_data.refresh_date == data["refresh_date"]

    @mock.patch.object(Ingestion, "to_model")
    def test_convert_to_models(self, spy_to_model: mock.MagicMock):
        """
        Given a list of dictionaries representing headline number records
        When `convert_to_models()` is called from an instance of `Ingestion`
        Then the call is delegated to the `to_models()` method for each entity

        Patches:
            `spy_to_model`: For the main assertion.
                To check each model is built via
                calls to `to_models()`

        """
        # Given
        mocked_raw_headline_one = mock.Mock()
        mocked_raw_headline_two = mock.Mock()
        data = [mocked_raw_headline_one, mocked_raw_headline_two]
        ingestion = Ingestion(data=data)

        # When
        converted_headlines = ingestion._convert_to_models(data)

        # Then
        expected_calls = [
            mock.call(data_record=mocked_raw_headline_one),
            mock.call(data_record=mocked_raw_headline_two),
        ]
        spy_to_model.assert_has_calls(expected_calls, any_order=True)

        assert converted_headlines == [spy_to_model.return_value] * 2

    @pytest.mark.parametrize(
        "attribute_on_class, expected_model_manager",
        [
            ("theme_manager", core_models.Theme.objects),
            ("sub_theme_manager", core_models.SubTheme.objects),
            ("topic_manager", core_models.Topic.objects),
            ("metric_group_manager", core_models.MetricGroup.objects),
            ("metric_manager", core_models.Metric.objects),
            ("geography_type_manager", core_models.GeographyType.objects),
            ("geography_manager", core_models.Geography.objects),
            ("age_manager", core_models.Age.objects),
            ("stratum_manager", core_models.Stratum.objects),
            ("core_headline_manager", core_models.CoreHeadline.objects),
        ],
    )
    def test_initializes_with_default_core_model_managers(
        self, attribute_on_class: str, expected_model_manager: Type[Manager]
    ):
        """
        Given an instance of `Ingestion`
        When the object is initialized
        Then the concrete core model managers
            are set on the `Ingestion` object
        """
        # Given
        mocked_data = mock.Mock()

        # When
        ingestion = Ingestion(data=mocked_data)

        # Then
        assert getattr(ingestion, attribute_on_class) is expected_model_manager

    def test_get_column_names_with_foreign_keys(self):
        """
        Given mocked data
        When the `column_names_with_foreign_keys` property
            is called from an instance of `Ingestion`
        Then the correct list of strings is returned
        """
        # Given
        mocked_data = mock.Mock()
        ingestion = Ingestion(data=mocked_data)

        # When
        returned_column_names: tuple[
            str, ...
        ] = ingestion.column_names_with_foreign_keys

        # Then
        assert returned_column_names == COLUMN_NAMES_WITH_FOREIGN_KEYS

    @mock.patch.object(Ingestion, "_remove_rows_with_nan_metric_value")
    def test_convert_df_to_models_calls_method_to_remove_nan_rows(
        self,
        spy_remove_rows_with_nan_metric_value: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `convert_df_to_models()` is called
            from an instance of `Ingestion`
        Then a call is delegated to the
            `_remove_rows_with_nan_metric_value()` method

        Patches:
            `spy_remove_rows_with_nan_metric_value`: For the
                main assertion
        """
        # Given
        mocked_dataframe = mock.Mock()
        ingestion = Ingestion(data=mock.Mock())

        # When
        ingestion.convert_df_to_models(dataframe=mocked_dataframe)

        # Then
        spy_remove_rows_with_nan_metric_value.assert_called_once_with(
            dataframe=mocked_dataframe
        )

    @mock.patch.object(Ingestion, "_remove_rows_with_nan_metric_value")
    @mock.patch.object(Ingestion, "_cast_int_type_on_columns_with_foreign_keys")
    def test_convert_df_to_models_calls_method_to_cast_int_type_to_columns(
        self,
        spy_cast_int_type_on_columns_with_foreign_keys: mock.MagicMock,
        spy_remove_rows_with_nan_metric_value: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `convert_df_to_models()` is called
            from an instance of `Ingestion`
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
        ingestion = Ingestion(data=mock.Mock())

        # When
        ingestion.convert_df_to_models(dataframe=mocked_dataframe)

        # Then
        dataframe_from_previous_callee_method = (
            spy_remove_rows_with_nan_metric_value.return_value
        )
        spy_cast_int_type_on_columns_with_foreign_keys.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch.object(Ingestion, "_cast_int_type_on_columns_with_foreign_keys")
    @mock.patch.object(Ingestion, "_create_named_tuple_iterable_from")
    def test_convert_df_to_models_calls_method_to_create_iterable(
        self,
        spy_create_named_tuple_iterable_from: mock.MagicMock,
        spy_cast_int_type_on_columns_with_foreign_keys: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `convert_df_to_models()` is called
            from an instance of `Ingestion`
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
        ingestion = Ingestion(data=mock.Mock())

        # When
        ingestion.convert_df_to_models(dataframe=mocked_dataframe)

        # Then
        dataframe_from_previous_callee_method = (
            spy_cast_int_type_on_columns_with_foreign_keys.return_value
        )
        spy_create_named_tuple_iterable_from.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch.object(Ingestion, "_create_named_tuple_iterable_from")
    @mock.patch.object(Ingestion, "_convert_to_models")
    def test_convert_df_to_models_calls_method_to_convert_to_models(
        self,
        spy_convert_to_models: mock.MagicMock,
        spy_create_named_tuple_iterable_from: mock.MagicMock,
    ):
        """
        Given a mocked `DataFrame`
        When `convert_df_to_models()` is called
            from an instance of `Ingestion`
        Then the final call is delegated to the
            `_convert_to_models()` method

        Patches:
            `spy_convert_to_models`: For
                the main assertion
            `spy_create_named_tuple_iterable_from`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_create_named_tuple_iterable_from()`

        """
        # Given
        mocked_dataframe = mock.MagicMock()
        ingestion = Ingestion(data=mock.Mock())

        # When
        ingestion.convert_df_to_models(dataframe=mocked_dataframe)

        # Then
        dataframe_from_previous_callee_method = (
            spy_create_named_tuple_iterable_from.return_value
        )
        spy_convert_to_models.assert_called_once_with(
            dataframe=dataframe_from_previous_callee_method
        )

    @mock.patch(f"{MODULE_PATH}.pd")
    def test_open_data_as_dataframe(self, spy_pandas: mock.MagicMock):
        """
        Given mocked data
        When `open_data_as_dataframe()` is called
            from an instance of `Ingestion`
        Then the call is delegated to `read_json()`
            from the `pandas` library

        Patches:
            `spy_pd`: For the main assertion of
                checking the contract with `read_json()`
                from the `pandas` library
        """
        # Given
        mocked_data = mock.Mock()
        ingestion = Ingestion(data=mocked_data)

        # When
        returned_dataframe = ingestion.open_data_as_dataframe()

        # Then
        spy_pandas.read_json.assert_called_once_with(mocked_data)
        assert returned_dataframe == spy_pandas.read_json.return_value

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
