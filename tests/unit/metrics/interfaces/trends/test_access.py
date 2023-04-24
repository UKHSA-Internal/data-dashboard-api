from unittest import mock

from metrics.domain.trends.state import Trend
from metrics.interfaces.trends.access import TrendsInterface
from tests.fakes.factories.core_time_series_factory import FakeCoreTimeSeriesFactory
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager


class TestTrendsInterface:
    def test_get_value_calls_model_manager_with_correct_args(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `get_value()` is called from an instance of the `TrendsInterface`
        Then the call is delegated to the `get_latest_metric_value()` method on the model manager
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "new_cases_7days_change"
        percentage_metric_name = "new_cases_7days_change_percentage"
        spy_core_time_series_manager = mock.Mock()

        interface = TrendsInterface(
            topic_name=topic_name,
            metric_name=metric_name,
            percentage_metric_name=percentage_metric_name,
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        value = interface.get_value(metric_to_lookup=metric_name)

        # Then
        spy_core_time_series_manager.get_latest_metric_value.assert_called_once_with(
            topic=topic_name, metric_name=metric_name
        )
        assert (
            value == spy_core_time_series_manager.get_latest_metric_value.return_value
        )

    def test_create_trend_returns_correct_object(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `create_trend()` is called from an instance of the `TrendsInterface`
        Then a `Trend` object is returned containing values retrieved by the model manager
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "new_cases_7days_change"
        percentage_metric_name = "new_cases_7days_change_percentage"

        (
            main_core_time_series,
            percentage_core_time_series,
        ) = FakeCoreTimeSeriesFactory.build_example_trend_type_records(
            metric_name=metric_name, percentage_metric_name=percentage_metric_name
        )

        interface = TrendsInterface(
            topic_name=topic_name,
            metric_name=metric_name,
            percentage_metric_name=percentage_metric_name,
            core_time_series_manager=FakeCoreTimeSeriesManager(
                time_series=[main_core_time_series, percentage_core_time_series]
            ),
        )

        # When
        trend = interface.create_trend()

        # Then
        assert type(trend) is Trend
        assert trend.metric_name == metric_name
        assert trend.percentage_metric_name == percentage_metric_name

        # Values match the associated `metric_value` fields on the records
        # fetched via the model manager
        assert trend.metric_value == main_core_time_series.metric_value
        assert trend.percentage_metric_value == percentage_core_time_series.metric_value
