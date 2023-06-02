import datetime
from typing import List
from unittest import mock

import plotly.graph_objects

from metrics.domain.charts.line_multi_coloured import generation
from metrics.domain.models import PlotParameters, PlotsCollection, PlotsData
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import (
    ChartsInterface,
    determine_last_updated,
    generate_chart,
    validate_chart_plot_parameters,
    validate_each_requested_chart_plot,
)
from metrics.interfaces.charts.validation import ChartsRequestValidator
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager

MODULE_PATH = "metrics.interfaces.charts.access"


class TestChartsInterface:
    @staticmethod
    def _setup_fake_time_series_for_plot(chart_plot_parameters: PlotParameters):
        return [
            FakeCoreTimeSeriesFactory.build_time_series(
                dt=datetime.date(year=2023, month=2, day=i + 1),
                metric_name=chart_plot_parameters.metric_name,
                topic_name=chart_plot_parameters.topic_name,
                stratum_name=chart_plot_parameters.stratum_name,
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

    @mock.patch.object(ChartsInterface, "generate_waffle_chart")
    def test_generate_chart_figure_delegates_call_for_waffle_chart(
        self,
        spy_generate_bar_chart_method: mock.MagicMock,
    ):
        """
        Given a requirement for a `waffle` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_waffle_chart()` method
        """
        # Given
        chart_type: str = ChartTypes.waffle.value
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

    @mock.patch.object(ChartsInterface, "generate_bar_chart")
    def test_generate_chart_figure_delegates_call_for_bar(
        self,
        spy_generate_bar_chart: mock.MagicMock,
    ):
        """
        Given a requirement for a `bar` chart
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
        spy_generate_bar_chart.assert_called_once()
        assert generated_chart_figure == spy_generate_bar_chart.return_value

    @mock.patch.object(ChartsInterface, "generate_line_multi_coloured_chart")
    def test_generate_chart_figure_delegates_call_for_line_multi_coloured(
        self,
        spy_generate_line_multi_coloured_chart_method: mock.MagicMock,
    ):
        """
        Given a requirement for a `line_multi_coloured` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_line_multi_coloured_chart()` method
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
        spy_generate_line_multi_coloured_chart_method.assert_called_once()
        assert (
            generated_chart_figure
            == spy_generate_line_multi_coloured_chart_method.return_value
        )

    @mock.patch(f"{MODULE_PATH}.line_multi_coloured.generate_chart_figure")
    def test_generate_line_multi_coloured_chart(
        self,
        spy_line_multi_coloured_generate_chart_figure: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given a valid `PlotParameters` for a `line_multi_coloured` chart
        When `generate_line_multi_coloured_chart()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_chart_figure()`
            from the `line_multi_coloured` module with the correct args
        """
        # Given
        fake_core_time_series_collection = self._setup_fake_time_series_for_plot(
            chart_plot_parameters=valid_plot_parameters
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            fake_core_time_series_collection
        )
        plots_collection = PlotsCollection(
            plots=[valid_plot_parameters],
            file_format="svg",
            chart_width=123,
            chart_height=456,
        )

        charts_interface = ChartsInterface(
            chart_plots=plots_collection,
            core_time_series_manager=fake_core_time_series_manager,
        )

        # When
        line_multi_coloured_chart = (
            charts_interface.generate_line_multi_coloured_chart()
        )

        # Then
        spy_line_multi_coloured_generate_chart_figure.assert_called_once_with(
            chart_height=plots_collection.chart_height,
            chart_width=plots_collection.chart_width,
            chart_plots_data=charts_interface.build_chart_plots_data(),
        )
        assert (
            line_multi_coloured_chart
            == spy_line_multi_coloured_generate_chart_figure.return_value
        )

    def test_build_chart_plots_data_delegates_to_plots_interface(
        self,
        fake_chart_plot_parameters: PlotParameters,
        fake_chart_plot_parameters_covid_cases: PlotParameters,
    ):
        """
        Given a `PlotsCollection` model which contains `PlotParameters` for 2 separate plots
        When `build_chart_plots_data()` is called from an instance of the `ChartsInterface`
        Then the calls are delegated to the `build_plots_data()` method on the `PlotsInterface`
            for each individual `PlotParameters` model
        """
        # Given
        spy_plots_interface = mock.Mock()
        fake_chart_plots = PlotsCollection(
            plots=[fake_chart_plot_parameters, fake_chart_plot_parameters_covid_cases],
            file_format="png",
            chart_width=123,
            chart_height=456,
        )

        charts_interface = ChartsInterface(
            chart_plots=fake_chart_plots,
            core_time_series_manager=mock.Mock(),
            plots_interface=spy_plots_interface,
        )

        # When
        plots_data = charts_interface.build_chart_plots_data()

        # Then
        spy_plots_interface.build_plots_data.assert_called_once()
        assert plots_data == spy_plots_interface.build_plots_data.return_value

    @mock.patch(f"{MODULE_PATH}.calculations.get_rolling_period_slice_for_metric")
    @mock.patch.object(ChartsInterface, "calculate_change_in_metric_value")
    def test_param_builder_for_line_with_shaded_section(
        self,
        mocked_calculate_change_in_metric_value: mock.MagicMock,
        mocked_get_rolling_period_slice_for_metric: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotsCollection` model representing the requested plot and its corresponding data
        When `param_builder_for_line_with_shaded_section()` is called from an instance of the `ChartsInterface`
        Then the returned dict contains the expected key-value pairs
        """
        # Given
        width = 123
        height = 456
        mocked_dates = mock.Mock()
        mocked_values = mock.Mock()
        fake_plot_data = PlotsData(
            parameters=fake_chart_plot_parameters,
            x_axis=mocked_dates,
            y_axis=mocked_values,
        )

        fake_chart_plots = PlotsCollection(
            plots=[fake_chart_plot_parameters],
            file_format="svg",
            chart_width=width,
            chart_height=height,
        )

        charts_interface = ChartsInterface(
            chart_plots=fake_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        # When
        params_for_line_graph = (
            charts_interface.param_builder_for_line_with_shaded_section(
                plot_data=fake_plot_data
            )
        )

        # When
        metric: str = fake_plot_data.parameters.metric_name
        expected_constructed_params = {
            "chart_width": width,
            "chart_height": height,
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

    def test_plots_interface_is_created_with_correct_args_by_default(self):
        """
        Given a `PlotsCollection` and a `CoreTimeSeriesManager`
        When an instance of the `ChartsInterface` is created
            without explicitly providing a `PlotsInterface`
        Then an instance of the `PlotsInterface` is created with the correct args
        """
        # Given
        mocked_plots_collection = mock.MagicMock()
        mocked_core_time_series_manager = mock.Mock()

        # When
        charts_interface = ChartsInterface(
            chart_plots=mocked_plots_collection,
            core_time_series_manager=mocked_core_time_series_manager,
        )

        # Then
        created_plots_interface = charts_interface.plots_interface
        assert created_plots_interface.plots_collection == mocked_plots_collection
        assert (
            created_plots_interface.core_time_series_manager
            == mocked_core_time_series_manager
        )


class TestGenerateChart:
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_chart_plot")
    def test_delegates_call_for_validation(
        self,
        spy_validate_each_requested_chart_plot: mock.MagicMock,
        spy_generate_chart_figure: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart()` is called
        Then a call is delegated to `validate_each_requested_chart_plot()` for validation purposes
        And `generate_chart_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_chart(chart_plots=mocked_chart_plots)

        # Then
        spy_validate_each_requested_chart_plot.assert_called_once_with(
            chart_plots=mocked_chart_plots
        )
        spy_generate_chart_figure.assert_called_once_with()

    @mock.patch(f"{MODULE_PATH}.write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_chart_plot")
    def test_delegates_call_for_writing_the_chart_figure_to_file(
        self,
        mocked_validate_each_requested_chart_plot: mock.MagicMock,
        spy_generate_chart_figure: mock.MagicMock,
        spy_write_figure: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart()` is called
        Then a call is delegated to `validate_each_requested_chart_plot()` for validation purposes
        And `generate_chart_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_chart(chart_plots=mocked_chart_plots)

        # Then
        spy_write_figure.assert_called_once_with(
            figure=spy_generate_chart_figure.return_value,
            topic="-",
            file_format=mocked_chart_plots.file_format,
        )


class TestValidateEachRequestedChartPlot:
    @mock.patch(f"{MODULE_PATH}.validate_chart_plot_parameters")
    def test_delegates_call_for_each_chart_plot(
        self,
        spy_validate_chart_plot_parameters: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
        fake_chart_plot_parameters_covid_cases: PlotParameters,
    ):
        """
        Given a `PlotsCollection` model requesting plots
            of multiple `PlotParameters` models
        When `validate_each_requested_chart_plot()` is called
        Then the call is delegated to `validate_chart_plot_parameters()`
            for each `PlotParameters` models
        """
        # Given
        fake_requested_chart_plots = [
            fake_chart_plot_parameters,
            fake_chart_plot_parameters_covid_cases,
        ]
        fake_chart_plots = PlotsCollection(
            file_format="svg",
            plots=fake_requested_chart_plots,
            chart_width=123,
            chart_height=456,
        )

        # When
        validate_each_requested_chart_plot(chart_plots=fake_chart_plots)

        # Then
        expected_calls = [
            mock.call(chart_plot_parameters=requested_chart_plot)
            for requested_chart_plot in fake_requested_chart_plots
        ]
        spy_validate_chart_plot_parameters.assert_has_calls(calls=expected_calls)


class TestValidateChartPlotParameters:
    @mock.patch.object(ChartsRequestValidator, "validate")
    def test_delegates_call_to_validate_method_on_charts_request_validator_class(
        self,
        spy_validate_method: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotParameters` model
        When `validate_chart_plot_parameters()` is called
        Then the call is delegated to the `validate()` from an instance of the `ChartsRequestValidator`
        """
        # Given
        chart_plot_parameters = fake_chart_plot_parameters

        # When
        validate_chart_plot_parameters(chart_plot_parameters=chart_plot_parameters)

        # Then
        spy_validate_method.assert_called_once()


class TestLastUpdated:
    plot_1_dates: List[datetime.date] = [
        datetime.date(2022, 9, 5),
        datetime.date(2022, 9, 19),
        datetime.date(2022, 10, 3),
        datetime.date(2022, 10, 7),
        datetime.date(2022, 10, 21),
        datetime.date(2022, 11, 3),
        datetime.date(2022, 11, 14),
        datetime.date(2022, 12, 12),
        datetime.date(2022, 12, 26),
        datetime.date(2023, 1, 9),
    ]
    plot_1_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    plot_2_dates: List[datetime.date] = [
        datetime.date(2020, 9, 5),
        datetime.date(2022, 9, 19),
        datetime.date(2023, 3, 9),
    ]
    plot_2_values = [10, 20, 30]

    @staticmethod
    def _create_chart_plot_data(
        x_axis: List[datetime.date],
        y_axis: List[int],
    ) -> PlotsData:
        plot_params = PlotParameters(
            chart_type="line_multi_coloured",
            topic="RSV",
            metric="weekly_positivity_by_age",
        )
        return PlotsData(parameters=plot_params, x_axis=x_axis, y_axis=y_axis)

    def test_determine_last_updated_chart_has_dates(self):
        """
        Given a multi coloured line chart with two plots
        and with dates along the x axis
        When `determine_last_updated()` is called
        Then we get back the latest date along the x axis
        """

        # Given

        first_chart_plots_data = self._create_chart_plot_data(
            x_axis=self.plot_1_dates,
            y_axis=self.plot_1_values,
        )

        second_chart_plots_data = self._create_chart_plot_data(
            x_axis=self.plot_2_dates,
            y_axis=self.plot_2_values,
        )

        # When
        figure = generation.generate_chart_figure(
            chart_height=300,
            chart_width=400,
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        last_update_date: str = determine_last_updated(figure)

        # Then
        expected_date: str = "2023-03-09"

        assert last_update_date == expected_date

    def test_determine_last_updated_chart_does_not_have_dates(self):
        """
        Given a multi coloured line chart with two plots
        and with something other than dates along the x axis
        When `determine_last_updated()` is called
        Then we get back nothing
        """

        # Given

        first_chart_plots_data = self._create_chart_plot_data(
            x_axis=self.plot_1_dates,
            y_axis=self.plot_1_values,
        )

        second_chart_plots_data = self._create_chart_plot_data(
            x_axis=self.plot_2_dates,
            y_axis=self.plot_2_values,
        )

        # When
        figure = generation.generate_chart_figure(
            chart_height=300,
            chart_width=400,
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Simulate the chart has something other than dates along the x axis
        figure.update_xaxes({"type": "-"})

        last_update_date: str = determine_last_updated(figure)

        # Then
        expected_date: str = ""

        assert last_update_date == expected_date
