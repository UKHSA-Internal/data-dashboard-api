from typing import Type
from unittest import mock

import pytest
from django.db.models.manager import Manager

from ingestion.consumer import HeadlineDTO, Ingestion, Reader
from metrics.data.models import core_models

MODULE_PATH = "ingestion.consumer"


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

    @mock.patch.object(Ingestion, "create_dtos_from_source")
    @mock.patch(f"{MODULE_PATH}.create_core_headlines")
    def test_create_headlines_delegates_call_correctly(
        self,
        spy_create_core_headlines: mock.MagicMock,
        spy_create_dtos_from_source: mock.MagicMock,
    ):
        """
        Given mocked data
        When `create_headlines()` is called
            from an instance of `Ingestion`
        Then the call is delegated
            to `create_core_headlines()`
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
        expected_headline_dtos = spy_create_dtos_from_source.return_value
        spy_create_core_headlines.assert_called_once_with(
            headline_dtos=expected_headline_dtos,
            core_headline_manager=mocked_core_headline_manager,
            batch_size=batch_size,
        )
