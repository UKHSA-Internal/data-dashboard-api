from typing import Dict, List, Set, Tuple, Type, Union
from unittest import mock

import pytest
from django.db.models.manager import Manager

from metrics.data.models import core_models
from metrics.data.operations.ingestion import HeadlineDTO, Ingestion


@pytest.fixture
def example_headline_data_json() -> List[Dict[str, float]]:
    return [
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "headline",
            "metric": "COVID-19_headline_positivity_latest",
            "geography_type": "Lower Tier Local Authority",
            "geography": "Babergh",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "period_start": "2023-06-05",
            "period_end": "2023-06-11",
            "metric_value": 0.087,
            "refresh_date": "2023-06-21",
        },
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "headline",
            "metric": "COVID-19_headline_positivity_latest",
            "geography_type": "UKHSA Region",
            "geography": "Yorkshire and Humber",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "period_start": "2023-06-05",
            "period_end": "2023-06-11",
            "metric_value": 0.0639,
            "refresh_date": "2023-06-21",
        },
    ]


class TestIngestion:
    def test_to_model(self, example_headline_data_json):
        """
        Given a single headline record as a dictionary
        When `to_model()` is called from an instance of `Ingestion`
        Then the returned model is enriched with the correct fields
        """
        # Given
        data = example_headline_data_json
        headline_data = data[0]
        ingestion = Ingestion(data=data)

        # When
        model: HeadlineDTO = ingestion.to_model(data=headline_data)

        # Then
        assert model.theme == headline_data["parent_theme"]
        assert model.sub_theme == headline_data["child_theme"]
        assert model.metric_group == headline_data["metric_group"]
        assert model.topic == headline_data["topic"]
        assert model.metric == headline_data["metric"]
        assert model.geography_type == headline_data["geography_type"]
        assert model.geography == headline_data["geography"]
        assert model.age == headline_data["age"]
        assert model.sex == headline_data["sex"]
        assert model.stratum == headline_data["stratum"]
        assert model.period_start == headline_data["period_start"]
        assert model.period_end == headline_data["period_end"]
        assert model.metric_value == headline_data["metric_value"]
        assert model.refresh_date == headline_data["refresh_date"]

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
        converted_headlines = ingestion.convert_to_models()

        # Then
        expected_calls = [
            mock.call(mocked_raw_headline_one),
            mock.call(mocked_raw_headline_two),
        ]
        spy_to_model.assert_has_calls(expected_calls, any_order=True)

        assert converted_headlines == [spy_to_model.return_value] * 2

    @pytest.mark.parametrize(
        "fields, expected_unique_values",
        [
            (["theme"], {("infectious_disease",)}),
            (["theme", "sub_theme"], {("infectious_disease", "respiratory")}),
            (["topic", "sub_theme"], {("COVID-19", "respiratory")}),
            (["geography_type"], {("UKHSA Region",), ("Lower Tier Local Authority",)}),
            (
                ["geography", "geography_type"],
                {
                    (
                        "Yorkshire and Humber",
                        "UKHSA Region",
                    ),
                    (
                        "Babergh",
                        "Lower Tier Local Authority",
                    ),
                },
            ),
            (
                ["metric", "metric_group", "topic"],
                {("COVID-19_headline_positivity_latest", "headline", "COVID-19")},
            ),
            (
                ["metric_group", "topic"],
                {("headline", "COVID-19")},
            ),
            (["stratum"], {("default",)}),
            (["age"], {("all",)}),
        ],
    )
    def test_get_all_unique_values_for_fields(
        self,
        fields: List[str],
        expected_unique_values: Set[Tuple[str, ...]],
        example_headline_data_json: List[Dict[str, Union[str, float]]],
    ):
        """
        Given some sample headline data
        And a list of fields to get corresponding unique values for
        When `get_unique_values_for_fields()` is called
            from an instance of `Ingestion`
        Then a set of correct values is returned
        """
        # Given
        ingestion = Ingestion(data=example_headline_data_json)

        # When
        unique_values_for_keys: Set[
            Tuple[str, ...]
        ] = ingestion.get_unique_values_for_fields(fields)

        # Then
        assert unique_values_for_keys == expected_unique_values

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
            ("core_time_series_manager", core_models.CoreTimeSeries.objects),
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
