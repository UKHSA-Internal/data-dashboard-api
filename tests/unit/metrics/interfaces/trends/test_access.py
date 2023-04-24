from unittest import mock

import pytest

from metrics.domain.trends.state import Trend
from metrics.interfaces.trends import access
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
        value = interface.get_latest_metric_value(metric_to_lookup=metric_name)

        # Then
        spy_core_time_series_manager.get_latest_metric_value.assert_called_once_with(
            topic=topic_name, metric_name=metric_name
        )
        assert (
            value == spy_core_time_series_manager.get_latest_metric_value.return_value
        )

    def test_get_trend_returns_correct_object(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `get_trend()` is called from an instance of the `TrendsInterface`
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
        trend = interface.get_trend()

        # Then
        assert type(trend) is Trend
        assert trend.metric_name == metric_name
        assert trend.percentage_metric_name == percentage_metric_name

        # Values match the associated `metric_value` fields on the records
        # fetched via the model manager
        assert trend.metric_value == main_core_time_series.metric_value
        assert trend.percentage_metric_value == percentage_core_time_series.metric_value

    def test_get_latest_metric_value_raises_error_when_model_manager_returns_no_data(
        self,
    ):
        """
        Given a `CoreTimeSeriesManager` which returns no data when called
        When `get_latest_metric_value()` is called from an instance of `TrendsInterface`
        Then a `TrendNumberDataNotFoundError` is raised
        """
        # Given
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])
        fake_metric_name = "weekly_positivity"
        fake_topic_name = "COVID-19"

        headlines_interface = access.TrendsInterface(
            topic_name=fake_topic_name,
            metric_name=fake_metric_name,
            percentage_metric_name=mock.Mock(),
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When / Then
        expected_error_message = (
            f"Data for `{fake_topic_name}` and `{fake_metric_name}` could not be found."
        )
        with pytest.raises(
            access.TrendNumberDataNotFoundError, match=expected_error_message
        ):
            headlines_interface.get_latest_metric_value(fake_metric_name)


class TestTrendNumbers:
    @mock.patch.object(access.TrendsInterface, "get_trend")
    def test_delegates_call_to_interface_to_get_metric_value(
        self, spy_get_trend: mock.MagicMock
    ):
        """
        Given a `topic`, `metric_name` and `percentage_metric_name`
        When `generate_trend_numbers()` is called
        Then the call is delegated to `get_trend()` from an instance of the `TrendsInterface`
            which is subsequently used to call and return `dict()` from the `Trend` model
        """
        # Given
        mocked_topic = mock.Mock()
        mocked_metric_name = mock.Mock()
        mocked_percentage_metric_name = mock.Mock()

        # When
        trend_data = access.generate_trend_numbers(
            topic=mocked_topic,
            metric_name=mocked_metric_name,
            percentage_metric_name=mocked_percentage_metric_name,
        )

        # Then
        spy_get_trend.assert_called_once()
        mocked_trend = spy_get_trend.return_value

        assert trend_data == mocked_trend.dict.return_value
