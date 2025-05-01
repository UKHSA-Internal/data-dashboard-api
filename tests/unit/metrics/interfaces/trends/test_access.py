from unittest import mock

import pytest

from metrics.data.models.core_models import CoreHeadline
from metrics.domain.models.trends import TrendsParameters
from metrics.domain.trends.state import Trend
from metrics.interfaces.trends import access
from metrics.interfaces.trends.access import TrendsInterface
from tests.fakes.factories.metrics.headline_factory import FakeCoreHeadlineFactory
from tests.fakes.managers.headline_manager import FakeCoreHeadlineManager


class TestTrendsInterface:
    @property
    def example_trend_parameters(self) -> TrendsParameters:
        return TrendsParameters(
            topic="COVID-19",
            metric="COVID-19_headline_ONSdeaths_7DayChange",
            percentage_metric="COVID-19_headline_ONSdeaths_7DayPercentChange",
            geography="England",
            geography_type="Nation",
            stratum="default",
            age="all",
            sex="all",
        )

    def test_get_value_calls_model_manager_with_correct_args(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `get_value()` is called from an instance of the `TrendsInterface`
        Then the call is delegated to the `get_latest_metric_value()` method on the model manager
        """
        # Given
        trend_parameters = self.example_trend_parameters
        spy_core_headline_manager = mock.Mock()

        interface = TrendsInterface(
            trend_parameters=trend_parameters,
            core_headline_manager=spy_core_headline_manager,
        )

        # When
        value = interface.get_latest_metric_value(
            params=trend_parameters.to_dict_for_main_metric_query()
        )

        # Then
        spy_core_headline_manager.get_latest_headline.assert_called_once_with(
            **trend_parameters.to_dict_for_main_metric_query(),
        )
        assert value == spy_core_headline_manager.get_latest_headline.return_value

    def test_get_trend_returns_correct_object(self):
        """
        Given the names of a `topic`, `metric_name` and `percentage_metric_name`
        When `get_trend()` is called from an instance of the `TrendsInterface`
        Then a `Trend` object is returned containing values retrieved by the model manager
        """
        # Given
        trend_parameters = self.example_trend_parameters
        metric_name = trend_parameters.metric_name
        percentage_metric_name = trend_parameters.percentage_metric_name
        params = trend_parameters.to_dict_for_main_metric_query()
        params.pop("rbac_permissions")
        params["percentage_metric_name"] = percentage_metric_name

        period_end = "2024-02-29"
        params_to_build_headlines = {**params, "period_end": period_end}
        (
            main_core_headline,
            percentage_core_headline,
        ) = FakeCoreHeadlineFactory.build_example_trend_type_records(
            **params_to_build_headlines
        )

        interface = TrendsInterface(
            trend_parameters=trend_parameters,
            core_headline_manager=FakeCoreHeadlineManager(
                headlines=[main_core_headline, percentage_core_headline]
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
        assert trend.metric_value == main_core_headline.metric_value
        assert trend.percentage_metric_value == percentage_core_headline.metric_value

        assert str(trend.metric_period_end) == period_end
        assert str(trend.percentage_metric_period_end) == period_end

    def test_get_latest_metric_value_raises_error_when_model_manager_returns_no_data(
        self,
    ):
        """
        Given a `CoreTimeSeriesManager` which returns no data when called
        When `get_latest_metric_value()` is called from an instance of `TrendsInterface`
        Then a `TrendNumberDataNotFoundError` is raised
        """
        # Given
        trend_parameters = self.example_trend_parameters
        fake_core_headline_manager = FakeCoreHeadlineManager(headlines=[])

        trends_interface = access.TrendsInterface(
            trend_parameters=trend_parameters,
            core_headline_manager=fake_core_headline_manager,
        )

        # When / Then
        with pytest.raises(access.TrendNumberDataNotFoundError):
            trends_interface.get_latest_metric_value(
                params=trend_parameters.to_dict_for_main_metric_query()
            )

    def test_initializes_with_default_core_headline_manager(self):
        """
        Given a fake set of arguments
        When an instance of the `TrendsInterface` is created
        Then the default `CoreHeadlineManager`
            is set on the `TrendsInterface` object
        """
        trend_parameters = self.example_trend_parameters

        # When
        trends_interface = TrendsInterface(trend_parameters=trend_parameters)

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
        mocked_trend_parameters = mock.Mock()

        # When
        trend_data = access.generate_trend_numbers(
            trend_parameters=mocked_trend_parameters
        )

        # Then
        spy_get_trend.assert_called_once()
        mocked_trend = spy_get_trend.return_value

        assert trend_data == mocked_trend.model_dump.return_value
