from unittest import mock

import pytest

from metrics.data.models.core_models import CoreHeadline
from metrics.domain.trends.state import Trend
from metrics.interfaces.trends import access
from metrics.interfaces.trends.access import TrendsInterface
from tests.fakes.factories.metrics.headline_factory import FakeCoreHeadlineFactory
from tests.fakes.managers.headline_manager import FakeCoreHeadlineManager


class TestTrendsInterfaceBeta:
    @property
    def example_args(self) -> dict[str, str]:
        return {
            "topic_name": "COVID-19",
            "metric_name": "COVID-19_headline_ONSdeaths_7DayChange",
            "percentage_metric_name": "COVID-19_headline_ONSdeaths_7DayPercentChange",
            "geography_name": "England",
            "geography_type_name": "Nation",
            "stratum_name": "default",
            "age": "all",
            "sex": "all",
        }

    def test_get_value_calls_model_manager_with_correct_args(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `get_value()` is called from an instance of the `TrendsInterface`
        Then the call is delegated to the `get_latest_metric_value()` method on the model manager
        """
        # Given
        expected_args = self.example_args
        spy_core_headline_manager = mock.Mock()

        interface = TrendsInterface(
            **expected_args,
            core_headline_manager=spy_core_headline_manager,
        )

        # When
        value = interface.get_latest_metric_value(
            metric_name=expected_args["metric_name"]
        )

        # Then
        expected_args = self.example_args
        expected_args.pop("percentage_metric_name")
        spy_core_headline_manager.get_latest_metric_value.assert_called_once_with(
            **expected_args,
        )
        assert value == spy_core_headline_manager.get_latest_metric_value.return_value

    def test_get_trend_returns_correct_object(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `get_trend()` is called from an instance of the `TrendsInterface`
        Then a `Trend` object is returned containing values retrieved by the model manager
        """
        # Given
        example_args = self.example_args
        metric_name = example_args["metric_name"]
        percentage_metric_name = example_args["percentage_metric_name"]

        (
            main_core_time_series,
            percentage_core_time_series,
        ) = FakeCoreHeadlineFactory.build_example_trend_type_records(**example_args)

        interface = TrendsInterface(
            **example_args,
            core_headline_manager=FakeCoreHeadlineManager(
                headlines=[main_core_time_series, percentage_core_time_series]
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
        example_args = self.example_args
        fake_core_headline_manager = FakeCoreHeadlineManager(headlines=[])
        metric_name = example_args["metric_name"]

        headlines_interface = access.TrendsInterface(
            **example_args,
            core_headline_manager=fake_core_headline_manager,
        )

        # When / Then
        with pytest.raises(access.TrendNumberDataNotFoundError):
            headlines_interface.get_latest_metric_value(metric_name)

    def test_initializes_with_default_core_headline_manager(self):
        """
        Given a fake set of arguments
        When an instance of the `TrendsInterface` is created
        Then the default `CoreHeadlineManager`
            is set on the `TrendsInterface` object
        """
        example_args = self.example_args

        # When
        trends_interface = TrendsInterface(**example_args)

        # Then
        assert trends_interface.core_headline_manager == CoreHeadline.objects


class TestGenerateTrendNumbers:
    @mock.patch.object(access.TrendsInterface, "get_trend")
    def test_delegates_call_to_interface_to_get_metric_values(
        self, spy_get_trend: mock.MagicMock
    ):
        """
        Given a `topic`, `metric_name` and `percentage_metric_name`
        When `generate_trend_numbers()` is called
        Then the call is delegated to `get_trend()` from an instance of the `TrendsInterface`
            which is subsequently used to call and return `model_dump()` from the `Trend` model
        """
        # Given
        mocked_topic = mock.Mock()
        mocked_metric_name = mock.Mock()
        mocked_percentage_metric_name = mock.Mock()
        geography_name = mock.Mock()
        geography_type_name = mock.Mock()
        stratum_name = mock.Mock()
        sex = mock.Mock()
        age = mock.Mock()

        # When
        trend_data = access.generate_trend_numbers(
            topic_name=mocked_topic,
            metric_name=mocked_metric_name,
            percentage_metric_name=mocked_percentage_metric_name,
            geography_name=geography_name,
            geography_type_name=geography_type_name,
            stratum_name=stratum_name,
            sex=sex,
            age=age,
        )

        # Then
        spy_get_trend.assert_called_once()
        mocked_trend = spy_get_trend.return_value

        assert trend_data == mocked_trend.model_dump.return_value
