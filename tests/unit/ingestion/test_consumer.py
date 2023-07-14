from typing import Type
from unittest import mock

import pytest
from django.db.models.manager import Manager

from ingestion.consumer import FieldsAndModelManager, HeadlineDTO, Ingestion, Reader
from ingestion.data_transfer_models import TimeSeriesDTO
from metrics.data.models import core_models

MODULE_PATH = "ingestion.consumer"


class TestIngestion:
    # Headline DTO construction tests
    def test_to_headline_dto(self, example_headline_data):
        """
        Given a single headline record as a dictionary
        When `to_headline_dto()` is called from an instance of `Ingestion`
        Then the returned model is enriched with the correct fields
        """
        # Given
        data = example_headline_data[0]
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
        model: HeadlineDTO = ingestion.to_headline_dto(data_record=headline_data)

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

    @mock.patch.object(Ingestion, "to_headline_dto")
    def test_convert_to_headline_dtos(self, spy_to_headline_dto: mock.MagicMock):
        """
        Given a list of dictionaries representing headline number records
        When `_convert_to_headline_dtos()` is called from an instance of `Ingestion`
        Then the call is delegated to the `to_headline_dto()` method for each entity

        Patches:
            `spy_to_headline_dto`: For the main assertion.
                To check each `HeadlineDTO` is built via
                calls to `to_headline_dto()`

        """
        # Given
        mocked_raw_headline_one = mock.Mock()
        mocked_raw_headline_two = mock.Mock()
        data = [mocked_raw_headline_one, mocked_raw_headline_two]
        ingestion = Ingestion(data=data)

        # When
        converted_headline_dtos = ingestion._convert_to_headline_dtos(data)

        # Then
        expected_calls = [
            mock.call(data_record=mocked_raw_headline_one),
            mock.call(data_record=mocked_raw_headline_two),
        ]
        spy_to_headline_dto.assert_has_calls(expected_calls, any_order=True)

        assert converted_headline_dtos == [spy_to_headline_dto.return_value] * 2

    # Timeseries DTO construction tests

    def test_to_timeseries_dto(
        self, example_timeseries_data
    ):
        """
        Given a single timeseries record as a dictionary
        When `to_timeseries_dto()` is called from an instance of `Ingestion`
        Then the returned model is enriched with the correct fields
        """
        # Given
        data = example_timeseries_data[0]
        timeseries_data = mock.Mock(
            parent_theme=data["parent_theme"],
            child_theme=data["child_theme"],
            metric_group=data["metric_group"],
            topic=data["topic"],
            metric=data["metric"],
            geography_type=data["geography_type"],
            geography=data["geography"],
            geography_code=data["geography_code"],
            age=data["age"],
            sex=data["sex"],
            stratum=data["stratum"],
            metric_frequency=data["metric_frequency"],
            year=data["year"],
            month=data["month"],
            epiweek=data["epiweek"],
            date=data["date"],
            metric_value=data["metric_value"],
            refresh_date=data["refresh_date"],
        )
        ingestion = Ingestion(data=data)

        # When
        model: TimeSeriesDTO = ingestion.to_timeseries_dto(data_record=timeseries_data)

        # Then
        assert model.theme == timeseries_data.parent_theme == data["parent_theme"]
        assert model.sub_theme == timeseries_data.child_theme == data["child_theme"]
        assert (
            model.metric_group == timeseries_data.metric_group == data["metric_group"]
        )
        assert model.topic == timeseries_data.topic == data["topic"]
        assert model.metric == timeseries_data.metric == data["metric"]
        assert (
            model.geography_type
            == timeseries_data.geography_type
            == data["geography_type"]
        )
        assert model.geography == timeseries_data.geography == data["geography"]
        assert model.age == timeseries_data.age == data["age"]
        assert model.sex == timeseries_data.sex == data["sex"]
        assert model.stratum == timeseries_data.stratum == data["stratum"]
        assert (
            model.metric_frequency
            == timeseries_data.metric_frequency
            == data["metric_frequency"]
        )
        assert model.epiweek == timeseries_data.epiweek == data["epiweek"]
        assert model.month == timeseries_data.month == data["month"]
        assert model.year == timeseries_data.year == data["year"]
        assert (
            model.metric_value == timeseries_data.metric_value == data["metric_value"]
        )

    @mock.patch.object(Ingestion, "to_timeseries_dto")
    def test_convert_to_timeseries_dtos(self, spy_to_timeseries_dto: mock.MagicMock):
        """
        Given a list of dictionaries representing timeseries records
        When `_convert_to_timeseries_dtos()` is called from an instance of `Ingestion`
        Then the call is delegated to the `to_timeseries_dto()` method for each entity

        Patches:
            `spy_to_timeseries_dto`: For the main assertion.
                To check each `TimeSeriesDTO` is built via
                calls to `to_timeseries_dto()`

        """
        # Given
        mocked_raw_timeseries_one = mock.Mock()
        mocked_raw_timeseries_two = mock.Mock()
        data = [mocked_raw_timeseries_one, mocked_raw_timeseries_two]
        ingestion = Ingestion(data=data)

        # When
        converted_timeseries_dtos = ingestion._convert_to_timeseries_dtos(data)

        # Then
        expected_calls = [
            mock.call(data_record=mocked_raw_timeseries_one),
            mock.call(data_record=mocked_raw_timeseries_two),
        ]
        spy_to_timeseries_dto.assert_has_calls(expected_calls, any_order=True)

        assert converted_timeseries_dtos == [spy_to_timeseries_dto.return_value] * 2

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
            ("core_timeseries_manager", core_models.CoreTimeSeries.objects),
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

    def test_initializes_with_default_reader(self):
        """
        Given an instance of `Ingestion`
        When the object is initialized
        Then a `Reader` object is set on the `Ingestion` object
        """
        # Given
        mocked_data = mock.Mock()

        # When
        ingestion = Ingestion(data=mocked_data)

        # Then
        assert type(ingestion.reader) is Reader

    @mock.patch.object(Ingestion, "create_headlines_dtos_from_source")
    @mock.patch(f"{MODULE_PATH}.CREATE_CORE_HEADLINES")
    def test_create_headlines_delegates_call_correctly(
        self,
        spy_create_core_headlines: mock.MagicMock,
        spy_create_headlines_dtos_from_source: mock.MagicMock,
    ):
        """
        Given mocked data
        When `create_headlines()` is called from an instance of `Ingestion`
        Then the call is delegated to `create_core_headlines()`
        """
        # Given
        mocked_core_headline_manager = mock.Mock()
        ingestion = Ingestion(
            data=mock.Mock(),
            reader=mock.Mock(),  # Stubbed
            core_headline_manager=mocked_core_headline_manager,
        )
        batch_size = 100

        # When
        ingestion.create_headlines()

        # Then
        expected_headline_dtos = spy_create_headlines_dtos_from_source.return_value
        spy_create_core_headlines.assert_called_once_with(
            headline_dtos=expected_headline_dtos,
            core_headline_manager=mocked_core_headline_manager,
            batch_size=batch_size,
        )

    @mock.patch.object(Ingestion, "create_timeseries_dtos_from_source")
    @mock.patch(f"{MODULE_PATH}.CREATE_CORE_TIMESERIES")
    def test_create_timeseries_delegates_call_correctly(
        self,
        spy_create_timeseries: mock.MagicMock,
        spy_create_timeseries_dtos_from_source: mock.MagicMock,
    ):
        """
        Given mocked data
        When `create_timeseries()` is called from an instance of `Ingestion`
        Then the call is delegated to `create_core_headlines()`
        """
        # Given
        mocked_core_timeseries_manager = mock.Mock()
        ingestion = Ingestion(
            data=mock.Mock(),
            reader=mock.Mock(),  # Stubbed
            core_timeseries_manager=mocked_core_timeseries_manager,
        )
        batch_size = 100

        # When
        ingestion.create_timeseries()

        # Then
        expected_timeseries_dtos = spy_create_timeseries_dtos_from_source.return_value
        spy_create_timeseries.assert_called_once_with(
            timeseries_dtos=expected_timeseries_dtos,
            core_timeseries_manager=mocked_core_timeseries_manager,
            batch_size=batch_size,
        )

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
