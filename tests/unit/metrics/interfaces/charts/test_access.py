import datetime
from unittest import mock

import plotly.graph_objects
import pytest

from metrics.domain.models import PlotData, PlotParameters, PlotsCollection
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import (
    ChartsInterface,
    InvalidFileFormatError,
    generate_chart_as_file,
    generate_encoded_chart,
)
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
                date=datetime.date(year=2023, month=2, day=i + 1),
                metric_name=chart_plot_parameters.metric_name,
                topic_name=chart_plot_parameters.topic_name,
                stratum_name=chart_plot_parameters.stratum_name,
            )
            for i in range(10)
        ]

    @mock.patch.object(ChartsInterface, "generate_simple_line_chart")
    def test_generate_chart_figure_delegates_call_for_simple_line_chart(
        self,
        spy_generate_simple_line_chart: mock.MagicMock,
    ):
        """
        Given a requirement for a `simple_line_graph` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_simple_line_chart()` method

        Patches:
            `spy_generate_simple_line_chart`: For the main assertion.
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
        spy_generate_simple_line_chart.assert_called_once()
        assert generated_chart_figure == spy_generate_simple_line_chart.return_value

    @mock.patch.object(ChartsInterface, "generate_line_with_shaded_section_chart")
    def test_generate_chart_figure_delegates_call_for_line_with_shaded_section_chart(
        self,
        spy_generate_line_with_shaded_section_chart: mock.MagicMock,
    ):
        """
        Given a requirement for a `line_with_shaded_section` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_line_with_shaded_section_chart()` method

        Patches:
            `spy_generate_line_with_shaded_section_chart`: For the main assertion.
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
        spy_generate_line_with_shaded_section_chart.assert_called_once()
        assert (
            generated_chart_figure
            == spy_generate_line_with_shaded_section_chart.return_value
        )

    @mock.patch.object(ChartsInterface, "generate_waffle_chart")
    def test_generate_chart_figure_delegates_call_for_waffle_chart(
        self,
        spy_generate_waffle_chart: mock.MagicMock,
    ):
        """
        Given a requirement for a `waffle` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_waffle_chart()` method

        Patches:
            `spy_generate_waffle_chart`: For the main assertion.
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
        spy_generate_waffle_chart.assert_called_once()
        assert generated_chart_figure == spy_generate_waffle_chart.return_value

    @mock.patch.object(ChartsInterface, "generate_bar_chart")
    def test_generate_chart_figure_delegates_call_for_bar(
        self,
        spy_generate_bar_chart: mock.MagicMock,
    ):
        """
        Given a requirement for a `bar` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_bar_chart()` method

        Patches:
            `spy_generate_bar_chart`: For the main assertion.
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

        Patches:
            `spy_generate_line_multi_coloured_chart_method`: For the
                main assertion.
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

    @mock.patch.object(ChartsInterface, "_set_latest_date_from_plots_data")
    @mock.patch(f"{MODULE_PATH}.line_multi_coloured.generate_chart_figure")
    def test_generate_line_multi_coloured_chart(
        self,
        spy_line_multi_coloured_generate_chart_figure: mock.MagicMock,
        mocked_set_latest_date_from_plots_data: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given a valid `PlotParameters` for a `line_multi_coloured` chart
        When `generate_line_multi_coloured_chart()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_chart_figure()`
            from the `line_multi_coloured` module with the correct args

        Patches:
            `spy_line_multi_coloured_generate_chart_figure`: For the
                main assertion.
            `mocked_set_latest_date_from_plots_data`: To isolate
                date conversion logic away from the scope of the test
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
            x_axis="date",
            y_axis="metric",
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

    @mock.patch.object(ChartsInterface, "_set_latest_date_from_plots_data")
    def test_build_chart_plots_data_delegates_to_plots_interface(
        self,
        spy_set_latest_date_from_plots_data: mock.MagicMock,
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
        spy_plots_interface = mock.MagicMock()
        fake_chart_plots = PlotsCollection(
            plots=[fake_chart_plot_parameters, fake_chart_plot_parameters_covid_cases],
            file_format="png",
            chart_width=123,
            chart_height=456,
            x_axis="date",
            y_axis="metric",
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
        # Check that the latest_date is set on the `ChartsInterface`
        spy_set_latest_date_from_plots_data.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.calculations.get_rolling_period_slice_for_metric")
    @mock.patch.object(ChartsInterface, "calculate_change_in_metric_value")
    def test_param_builder_for_line_with_shaded_section(
        self,
        spy_calculate_change_in_metric_value: mock.MagicMock,
        spy_get_rolling_period_slice_for_metric: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a `PlotsCollection` model representing the requested plot and its corresponding data
        When `param_builder_for_line_with_shaded_section()` is called from an instance of the `ChartsInterface`
        Then the returned dict contains the expected key-value pairs

        Patches:
            `spy_calculate_change_in_metric_value`: For one of the
                main assertions. To check this method is delegated
                to for the value of the "change_in_metric_value" field
            `spy_get_rolling_period_slice_for_metric`: For one of the
                main assertions. To check this method is delegated
                to for the value of the "rolling_period_slice" field
        """
        # Given
        width = 123
        height = 456
        mocked_x_axis_values = mock.Mock()
        mocked_y_axis_values = mock.Mock()
        fake_plot_data = PlotData(
            parameters=fake_chart_plot_parameters,
            x_axis_values=mocked_x_axis_values,
            y_axis_values=mocked_y_axis_values,
        )

        fake_chart_plots = PlotsCollection(
            plots=[fake_chart_plot_parameters],
            file_format="svg",
            chart_width=width,
            chart_height=height,
            x_axis="date",
            y_axis="metric",
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
            "x_axis_values": mocked_x_axis_values,
            "y_axis_values": mocked_y_axis_values,
            "metric_name": metric,
            "change_in_metric_value": spy_calculate_change_in_metric_value.return_value,
            "rolling_period_slice": spy_get_rolling_period_slice_for_metric.return_value,
        }
        assert params_for_line_graph == expected_constructed_params

        spy_calculate_change_in_metric_value.assert_called_once_with(
            values=mocked_y_axis_values,
            metric_name=metric,
        )
        spy_get_rolling_period_slice_for_metric.assert_called_once_with(
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

    @mock.patch.object(ChartsInterface, "create_optimized_svg", return_value="abc")
    def test_get_encoded_chart_delegates_call_to_get_last_updated(
        self,
        mocked_create_optimized_svg: mock.MagicMock,
    ):
        """
        Given a mocked figure which returns
        When `get_encoded_chart()` is called from an instance of the `ChartsInterface`
        Then the `last_updated` field is populated
            from the `_latest_date` attribute

        Patches:
            `mocked_create_optimized_svg`: To remove the side effect of
                creating a svg and optimizing it

        """
        # Given
        mocked_latest_date = mock.Mock()
        mocked_plots_collection = mock.MagicMock(file_format="svg")
        charts_interface = ChartsInterface(chart_plots=mocked_plots_collection)
        charts_interface._latest_date = mocked_latest_date

        # When
        encoded_chart: dict[str, str] = charts_interface.get_encoded_chart(
            figure=mock.Mock()
        )

        # Then
        assert encoded_chart["last_updated"] == mocked_latest_date

    @mock.patch.object(ChartsInterface, "encode_figure")
    def test_get_encoded_chart_delegates_call_to_encode_figure(
        self, spy_encode_figure: mock.MagicMock
    ):
        """
        Given a mocked figure
        When `get_encoded_chart()` is called from an instance of the `ChartsInterface`
        Then the `chart` field is populated via a call to the `encode_figure()` method

        Patches:
            `spy_encode_figure`: For the main assertion
        """
        # Given
        mocked_plots_collection = mock.MagicMock()
        mocked_figure = mock.Mock()
        mocked_figure.to_image.return_value = "abc"
        charts_interface = ChartsInterface(chart_plots=mocked_plots_collection)

        # When
        encoded_chart: dict[str, str] = charts_interface.get_encoded_chart(
            figure=mocked_figure
        )

        # Then
        assert encoded_chart["chart"] == spy_encode_figure.return_value


class TestGenerateChartAsFile:
    @mock.patch.object(ChartsInterface, "write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    def test_delegates_call_for_validation(
        self,
        spy_generate_chart_figure: mock.MagicMock,
        mocked_write_figure: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart_as_file()` is called
        Then `generate_chart_figure` is called
            from an instance of the `ChartsInterface`
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_chart_as_file(chart_plots=mocked_chart_plots)

        # Then
        spy_generate_chart_figure.assert_called_once_with()

    @mock.patch.object(ChartsInterface, "write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    def test_delegates_call_for_writing_the_chart(
        self,
        spy_generate_chart_figure: mock.MagicMock,
        spy_write_figure: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart_as_file()` is called
        Then `write_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_chart_as_file(chart_plots=mocked_chart_plots)

        # Then
        spy_write_figure.assert_called_once_with(
            figure=spy_generate_chart_figure.return_value,
        )


class TestGenerateEncodedChart:
    @mock.patch.object(ChartsInterface, "get_encoded_chart")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    def test_delegates_call_for_validation(
        self,
        spy_generate_chart_figure: mock.MagicMock,
        mocked_get_encoded_chart: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_encoded_chart()` is called
        Then a call is delegated to `generate_chart_figure`
            from an instance of the `ChartsInterface`

        Patches:
            `spy_generate_chart_figure`: For one of
                the main assertions
            `mocked_get_encoded_chart`: To remove the side effects
                of having to encode the chart figure
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_encoded_chart(chart_plots=mocked_chart_plots)

        # Then
        spy_generate_chart_figure.assert_called_once_with()

    @mock.patch.object(ChartsInterface, "get_encoded_chart")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    def test_delegates_call_to_get_encoded_chart(
        self,
        mocked_generate_chart_figure: mock.MagicMock,
        spy_get_encoded_chart: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_encoded_chart()` is called
        Then the call is delegated to `get_encoded_chart()`
            from an instance of the `ChartsInterface`

        Patches:
            `mocked_generate_chart_figure`: To set the returned figure
                so that it can encoded more easily
                and so the return value can be
                passed to the main assertion
            `spy_get_encoded_chart`: For the main assertion
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])
        mocked_figure = mock.Mock()
        mocked_figure.to_image.return_value = "abc"
        mocked_generate_chart_figure.return_value = mocked_figure

        # When
        generate_encoded_chart(chart_plots=mocked_chart_plots)

        # Then
        spy_get_encoded_chart.assert_called_once_with(
            figure=mocked_generate_chart_figure.return_value
        )


class TestMiscMethods:
    @pytest.mark.parametrize(
        "file_format",
        [
            "png",
            "jpg",
            "jpeg",
        ],
    )
    def test_invalid_format_passed_to_encode_figure(self, file_format: str):
        """
        Given the user supplies an invalid file_format to pass to encode_figure
        When `encode_figure` is called from an instance of the `ChartsInterface`
        Then an `InvalidFileFormatError` is raised
        """
        # Given
        mocked_chart_plot_params = mock.Mock(chart_type=ChartTypes.simple_line.value)
        mocked_chart_plots = mock.Mock(
            file_format=file_format,
            plots=[mocked_chart_plot_params],
        )

        charts_interface = ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        figure = plotly.graph_objs.Figure()

        # When / Then
        with pytest.raises(InvalidFileFormatError):
            charts_interface.encode_figure(figure=figure)
