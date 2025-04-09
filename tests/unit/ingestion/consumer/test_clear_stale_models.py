from unittest import mock

from ingestion.consumer import Consumer
from metrics.data.managers.api_models.time_series import APITimeSeriesManager
from metrics.data.managers.core_models.headline import CoreHeadlineManager
from metrics.data.managers.core_models.time_series import CoreTimeSeriesManager


class TestConsumerClearStaleModels:
    def test_clear_stale_headlines(self, example_headline_data: dict):
        """
        Given incoming headline data
        When `clear_stale_headlines()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `CoreHeadlineManager` with the correct args
        """
        # Given
        spy_core_headline_manager = mock.Mock(spec_set=CoreHeadlineManager)
        consumer = Consumer(
            source_data=example_headline_data,
            core_headline_manager=spy_core_headline_manager,
        )

        # When
        consumer.clear_stale_headlines()

        # Then
        expected_params = {
            "topic_name": example_headline_data["topic"],
            "metric_name": example_headline_data["metric"],
            "geography_name": example_headline_data["geography"],
            "geography_type_name": example_headline_data["geography_type"],
            "geography_code": example_headline_data["geography_code"],
            "stratum_name": example_headline_data["stratum"],
            "sex": example_headline_data["sex"],
            "age": example_headline_data["age"],
        }
        expected_calls = [
            mock.call(**expected_params, is_public=True),
            mock.call(**expected_params, is_public=False),
        ]
        spy_core_headline_manager.delete_superseded_data.assert_has_calls(
            calls=expected_calls
        )

    def test_clear_stale_timeseries(self, example_headline_data: dict):
        """
        Given incoming timeseries data
        When `clear_stale_timeseries()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `CoreTimeSeriesManager` with the correct args
        And a similar call is made to the `APITimeSeriesManager`
        """
        # Given
        spy_core_timeseries_manager = mock.Mock(spec_set=CoreTimeSeriesManager)
        spy_api_timeseries_manager = mock.Mock(spec_set=APITimeSeriesManager)
        consumer = Consumer(
            source_data=example_headline_data,
            core_timeseries_manager=spy_core_timeseries_manager,
            api_timeseries_manager=spy_api_timeseries_manager,
        )

        # When
        consumer.clear_stale_timeseries()

        # Then
        spy_core_timeseries_manager.delete_superseded_data.assert_called_once_with(
            metric_name=example_headline_data["metric"],
            geography_name=example_headline_data["geography"],
            geography_type_name=example_headline_data["geography_type"],
            geography_code=example_headline_data["geography_code"],
            stratum_name=example_headline_data["stratum"],
            sex=example_headline_data["sex"],
            age=example_headline_data["age"],
        )
        spy_api_timeseries_manager.delete_superseded_data.assert_called_once_with(
            theme_name=example_headline_data["parent_theme"],
            sub_theme_name=example_headline_data["child_theme"],
            topic_name=example_headline_data["topic"],
            metric_name=example_headline_data["metric"],
            geography_name=example_headline_data["geography"],
            geography_type_name=example_headline_data["geography_type"],
            geography_code=example_headline_data["geography_code"],
            stratum_name=example_headline_data["stratum"],
            sex=example_headline_data["sex"],
            age=example_headline_data["age"],
        )
