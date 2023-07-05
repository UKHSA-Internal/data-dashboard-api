from typing import Dict, List
from unittest import mock

import pytest

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
        }
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
