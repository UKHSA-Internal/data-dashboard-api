import datetime
from typing import List
from unittest import mock

import pytest

from metrics.domain.models import ChartPlotData, ChartPlotParameters, ChartPlots
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import (
    ChartsInterface,
    DataNotFoundError,
    make_datetime_from_string,
)
from tests.fakes.factories.core_time_series_factory import FakeCoreTimeSeriesFactory
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.models.core_time_series import FakeCoreTimeSeries

MODULE_PATH = "metrics.interfaces.charts.access"


class TestChartsInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(chart_plot_parameters: ChartPlotParameters):
        return [
            FakeCoreTimeSeriesFactory.build_time_series(
                dt=datetime.datetime(year=2023, month=1, day=i + 1),
                metric_name=chart_plot_parameters.metric,
                topic_name=chart_plot_parameters.topic,
                stratum_name=chart_plot_parameters.stratum,
            )
            for i in range(10)
        ]

    @mock.patch.object(ChartsInterface, "generate_simple_line_chart")
    def test_generate_chart_figure_delegates_call_for_simple_line_chart(
        self,
        spy_generate_simple_line_chart_method: mock.MagicMock,
    ):
        """
        Given a requirement for a `simple_line_graph` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_simple_line_chart()` method
        """
        # Given
        chart_type: str = ChartTypes.simple_line.value
        mocked_chart_plot_params = mock.Mock(chart_type=chart_type)
        mocked_chart_plots = mock.Mock(plots=[mocked_chart_plot_params])

        charts_interface = ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_figure = charts_interface.generate_chart_figure()

        # Then
        spy_generate_simple_line_chart_method.assert_called_once()
        assert (
            generated_chart_figure == spy_generate_simple_line_chart_method.return_value
        )

    @mock.patch.object(ChartsInterface, "generate_line_with_shaded_section_chart")
    def test_generate_chart_figure_delegates_call_for_line_with_shaded_section_chart(
        self,
        spy_generate_line_with_shaded_section_chart_method: mock.MagicMock,
    ):
        """
        Given a requirement for a `line_with_shaded_section` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_line_with_shaded_section_chart()` method
        """
        # Given
        chart_type: str = ChartTypes.line_with_shaded_section.value
        mocked_chart_plot_params = mock.Mock(chart_type=chart_type)
        mocked_chart_plots = mock.Mock(plots=[mocked_chart_plot_params])

        charts_interface = ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_figure = charts_interface.generate_chart_figure()

        # Then
        spy_generate_line_with_shaded_section_chart_method.assert_called_once()
        assert (
            generated_chart_figure
            == spy_generate_line_with_shaded_section_chart_method.return_value
        )

    @mock.patch.object(ChartsInterface, "generate_bar_chart")
    def test_generate_chart_figure_delegates_call_for_waffle_chart(
        self,
        spy_generate_bar_chart_method: mock.MagicMock,
    ):
        """
        Given a requirement for a `generate_bar_chart` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_bar_chart()` method
        """
        # Given
        chart_type: str = ChartTypes.bar.value
        mocked_chart_plot_params = mock.Mock(chart_type=chart_type)
        mocked_chart_plots = mock.Mock(plots=[mocked_chart_plot_params])

        charts_interface = ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_figure = charts_interface.generate_chart_figure()

        # Then
        spy_generate_bar_chart_method.assert_called_once()
        assert generated_chart_figure == spy_generate_bar_chart_method.return_value

    @mock.patch.object(ChartsInterface, "generate_line_multi_coloured")
    def test_generate_chart_figure_delegates_call_for_line_multi_coloured(
        self,
        spy_generate_line_multi_coloured_method: mock.MagicMock,
    ):
        """
        Given a requirement for a `line_multi_coloured` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_chart_figure()` method
        """
        # Given
        chart_type: str = ChartTypes.line_multi_coloured.value
        mocked_chart_plot_params = mock.Mock(chart_type=chart_type)
        mocked_chart_plots = mock.Mock(plots=[mocked_chart_plot_params])

        charts_interface = ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_figure = charts_interface.generate_chart_figure()

        # Then
        spy_generate_line_multi_coloured_method.assert_called_once()
        assert (
            generated_chart_figure
            == spy_generate_line_multi_coloured_method.return_value
        )

    @mock.patch.object(ChartsInterface, "build_chart_plot_data_from_parameters")
    def test_build_chart_plots_data_delegates_call_for_each_plot(
        self,
        mocked_build_chart_plot_data_from_parameters: mock.MagicMock,
        fake_chart_plot_parameters,
    ):
        """
        Given a `ChartPlots` model which contains `ChartPlotParameters` for 2 separate plots
        When `build_chart_plots_data()` is called from an instance of the `ChartsInterface`
        Then the calls are delegated to the `build_chart_plot_data_from_parameters()` method
            for each individual `ChartPlotParameters` model
        """
        # Given
        fake_chart_plot_parameter_second = ChartPlotParameters(
            chart_type="line_multi_coloured", topic="COVID-19", metric="new_cases_daily"
        )
        fake_chart_plots = ChartPlots(
            plots=[fake_chart_plot_parameters, fake_chart_plot_parameter_second],
            file_format="png",
        )

        charts_interface = ChartsInterface(
            chart_plots=fake_chart_plots, core_time_series_manager=mock.Mock()
        )

        # When
        chart_plots_data = charts_interface.build_chart_plots_data()

        # Then
        # Check that `build_chart_plot_data_from_parameters()` method
        # is called for each of the provided `ChartPlotParameters` models
        expected_calls = [
            mock.call(chart_plot_parameters=fake_chart_plot_parameters),
            mock.call(chart_plot_parameters=fake_chart_plot_parameter_second),
        ]
        mocked_build_chart_plot_data_from_parameters.assert_has_calls(
            calls=expected_calls,
            any_order=False,
        )

        expected_chart_plots_data = [
            mocked_build_chart_plot_data_from_parameters.return_value
        ] * 2
        assert chart_plots_data == expected_chart_plots_data

    def test_build_chart_plot_data_from_parameters(
        self, fake_chart_plot_parameters: ChartPlotParameters
    ):
        """
        Given a `ChartPlotParameters` model requesting a chart plot for existing `CoreTimeSeries`
        When `build_chart_plot_data_from_parameters()` is called from an instance of the `ChartsInterface`
        Then a `ChartPlotData` model is returned with the original parameters
        And the correct data passed to the `x_axis` and `y_axis`
        """
        # Given
        fake_chart_plots = ChartPlots(
            plots=[fake_chart_plot_parameters],
            file_format="png",
        )
        fake_core_time_series_for_plot: List[
            FakeCoreTimeSeries
        ] = self._setup_fake_time_series_for_plot(
            chart_plot_parameters=fake_chart_plot_parameters
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=fake_core_time_series_for_plot
        )

        charts_interface = ChartsInterface(
            chart_plots=fake_chart_plots,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        chart_plot_data: ChartPlotData = (
            charts_interface.build_chart_plot_data_from_parameters(
                chart_plot_parameters=fake_chart_plot_parameters
            )
        )

        # Then
        # Check that the parameters on the `ChartPlotData` model is ingested by the input `ChartPlotParameters` model
        assert chart_plot_data.parameters == fake_chart_plot_parameters

        # Check the correct data is passed to the axis of the `ChartPlotData` model
        assert chart_plot_data.x_axis == tuple(
            x.dt for x in fake_core_time_series_for_plot
        )
        assert chart_plot_data.y_axis == tuple(
            x.metric_value for x in fake_core_time_series_for_plot
        )

    def test_build_chart_plot_data_from_parameters_raises_error_when_no_data_found(
        self, fake_chart_plot_parameters: ChartPlotParameters
    ):
        """
        Given a `ChartPlotParameters` model requesting a chart plot for `CoreTimeSeries` data which cannot be found
        When `build_chart_plot_data_from_parameters()` is called from an instance of the `ChartsInterface`
        Then a `DataNotFoundError` is raised
        """
        # Given
        fake_chart_plots = ChartPlots(
            plots=[fake_chart_plot_parameters],
            file_format="png",
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(time_series=[])

        charts_interface = ChartsInterface(
            chart_plots=fake_chart_plots,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When / Then
        with pytest.raises(DataNotFoundError):
            charts_interface.build_chart_plot_data_from_parameters(
                chart_plot_parameters=fake_chart_plot_parameters
            )

    def test_get_timeseries_calls_core_time_series_manager_with_correct_args(self):
        """
        Given a `CoreTimeSeriesManager`
        When `get_timeseries()` is called from an instance of `ChartsInterface`
        Then the correct method is called from `CoreTimeSeriesManager` to retrieve the timeseries
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        mocked_date_from = mock.Mock()
        mocked_geography = mock.Mock()
        mocked_geography_type = mock.Mock()
        mocked_stratum = mock.Mock()

        charts_interface = ChartsInterface(
            chart_plots=mock.MagicMock(),
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        timeseries = charts_interface.get_timeseries(
            topic=mocked_topic,
            metric=mocked_metric,
            date_from=mocked_date_from,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            stratum=mocked_stratum,
        )

        # Then
        assert (
            timeseries
            == spy_core_time_series_manager.filter_for_dates_and_values.return_value
        )
        spy_core_time_series_manager.filter_for_dates_and_values.assert_called_once_with(
            topic=mocked_topic,
            metric=mocked_metric,
            date_from=mocked_date_from,
            geography=mocked_geography,
            geography_type=mocked_geography_type,
            stratum=mocked_stratum,
        )

    @mock.patch(f"{MODULE_PATH}.calculations.get_rolling_period_slice_for_metric")
    @mock.patch.object(ChartsInterface, "calculate_change_in_metric_value")
    def test_param_builder_for_line_with_shaded_section(
        self,
        mocked_calculate_change_in_metric_value: mock.MagicMock,
        mocked_get_rolling_period_slice_for_metric: mock.MagicMock,
        fake_chart_plot_parameters: ChartPlotParameters,
    ):
        """
        Given a `ChartPlotData` model representing the requested plot and its corresponding data
        When `param_builder_for_line_with_shaded_section()` is called from an instance of the `ChartsInterface`
        Then the returned dict contains the expected key-value pairs
        """
        # Given
        mocked_dates = mock.Mock()
        mocked_values = mock.Mock()
        fake_plot_data = ChartPlotData(
            parameters=fake_chart_plot_parameters,
            x_axis=mocked_dates,
            y_axis=mocked_values,
        )

        charts_interface = ChartsInterface(
            chart_plots=mock.MagicMock(),
            core_time_series_manager=mock.Mock(),
        )

        # When
        params_for_line_graph = (
            charts_interface.param_builder_for_line_with_shaded_section(
                plot_data=fake_plot_data
            )
        )

        # When
        metric: str = fake_plot_data.parameters.metric
        expected_constructed_params = {
            "dates": mocked_dates,
            "values": mocked_values,
            "metric_name": metric,
            "change_in_metric_value": mocked_calculate_change_in_metric_value.return_value,
            "rolling_period_slice": mocked_get_rolling_period_slice_for_metric.return_value,
        }
        assert params_for_line_graph == expected_constructed_params

        mocked_calculate_change_in_metric_value.assert_called_once_with(
            values=mocked_values,
            metric_name=metric,
        )
        mocked_get_rolling_period_slice_for_metric.assert_called_once_with(
            metric_name=metric
        )

    @mock.patch.object(ChartsInterface, "get_timeseries")
    def test_get_timeseries_for_chart_plot_parameters_delegates_call_with_correct_args(
        self,
        mocked_get_timeseries: mock.MagicMock,
        fake_chart_plot_parameters: ChartPlotParameters,
    ):
        """
        Given a `ChartPlotParameters` model with a defined `date_from`
        When `get_timeseries_for_chart_plot_parameters()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `get_timeseries()` method with the correct args
        """
        # Given
        date_from: str = "2023-01-01"
        fake_chart_plot_parameters.date_from = date_from

        charts_interface = ChartsInterface(
            chart_plots=mock.MagicMock(), core_time_series_manager=mock.Mock()
        )

        # When
        timeseries = charts_interface.get_timeseries_for_chart_plot_parameters(
            chart_plot_parameters=fake_chart_plot_parameters
        )

        # Then
        # The return value is delegated to the `get_timeseries` method
        assert timeseries == mocked_get_timeseries.return_value

        expected_date_from = make_datetime_from_string(date_from=date_from)
        # The dict representation of the `ChartPlotParameters` model
        # is unpacked into the `get_timeseries` method
        mocked_get_timeseries.assert_called_once_with(
            **fake_chart_plot_parameters.to_dict_for_query(),
            date_from=expected_date_from,
        )


class TestMakeDatetimeFromString:
    def test_returns_correct_value(self):
        """
        Given a valid date string in the format `%Y-%m-%d`
        When `make_datetime_from_string()` is called
        Then a `datetime.datetime` object is returned for the given date
        """
        # Given
        year = "2023"
        month = "01"
        day = "01"
        date_from = f"{year}-{month}-{day}"

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        assert type(parsed_date_from) == datetime.datetime
        assert parsed_date_from.year == int(year)
        assert parsed_date_from.month == int(month)
        assert parsed_date_from.day == int(day)

    @mock.patch(f"{MODULE_PATH}.get_date_n_months_ago_from_timestamp")
    def test_delegates_call_to_get_default_of_one_year_if_none_provided(
        self,
        spy_get_date_n_months_ago_from_timestamp: mock.MagicMock,
    ):
        """
        Given an input `date_from` of None
        When `make_datetime_from_string()` is called
        Then `get_date_n_months_ago_from_timestamp()` is called to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = None

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value

    @mock.patch(f"{MODULE_PATH}.get_date_n_months_ago_from_timestamp")
    def test_delegates_call_to_get_default_of_one_year_if_empty_string_provided(
        self,
        spy_get_date_n_months_ago_from_timestamp: mock.MagicMock,
    ):
        """
        Given an input `date_from` of an empty string
        When `make_datetime_from_string()` is called
        Then `get_date_n_months_ago_from_timestamp()` is called to make a datestamp of 1 year prior to the current date
        """
        # Given
        date_from = ""

        # When
        parsed_date_from = make_datetime_from_string(date_from=date_from)

        # Then
        spy_get_date_n_months_ago_from_timestamp.assert_called_once_with(
            datetime_stamp=datetime.date.today(),
            number_of_months=12,
        )
        assert parsed_date_from == spy_get_date_n_months_ago_from_timestamp.return_value
