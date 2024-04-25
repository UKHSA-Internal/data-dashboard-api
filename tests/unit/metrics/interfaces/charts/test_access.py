import datetime
from unittest import mock

import plotly.graph_objects
import pytest

from metrics.domain.models import PlotData, PlotParameters, PlotsCollection
from metrics.domain.common.utils import ChartTypes
from metrics.interfaces.charts.access import (
    ChartOutput,
    ChartsInterface,
    InvalidFileFormatError,
    generate_chart_as_file,
    generate_encoded_chart,
)
from metrics.interfaces.plots.access import InvalidPlotParametersError
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

    @mock.patch.object(ChartsInterface, "build_chart_plots_data")
    @mock.patch.object(ChartsInterface, "generate_line_with_shaded_section_chart")
    def test_generate_chart_figure_delegates_call_for_line_with_shaded_section_chart(
        self,
        spy_generate_line_with_shaded_section_chart: mock.MagicMock,
        mocked_build_chart_plots_data: mock.MagicMock,
        fake_plots_collection: PlotsCollection,
    ):
        """
        Given a requirement for a `line_with_shaded_section` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_line_with_shaded_section_chart()` method

        Patches:
            `spy_generate_line_with_shaded_section_chart`: For the main assertion.
            `mocked_build_chart_plots_data`: To remove the side effect
                of having to query the database for data relating to the chart

        """
        # Given
        fake_plots_collection.plots[0].chart_type = (
            ChartTypes.line_with_shaded_section.value
        )
        charts_interface = ChartsInterface(
            chart_plots=fake_plots_collection,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_output = charts_interface.generate_chart_output()

        # Then
        spy_generate_line_with_shaded_section_chart.assert_called_once_with(
            plots_data=mocked_build_chart_plots_data.return_value
        )
        chart_output = ChartOutput(
            figure=spy_generate_line_with_shaded_section_chart.return_value,
            description=charts_interface.build_chart_description(plots_data=[]),
        )
        assert generated_chart_output == chart_output

    @mock.patch.object(ChartsInterface, "build_chart_plots_data")
    @mock.patch.object(ChartsInterface, "generate_bar_chart")
    def test_generate_chart_figure_delegates_call_for_bar(
        self,
        spy_generate_bar_chart: mock.MagicMock,
        mocked_build_chart_plots_data: mock.MagicMock,
        fake_plots_collection: PlotsCollection,
    ):
        """
        Given a requirement for a `bar` chart
        When `generate_chart_figure()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_bar_chart()` method

        Patches:
            `spy_generate_bar_chart`: For the main assertion.
            `mocked_build_chart_plots_data`: To remove the side effect
                of having to query the database for data relating to the chart

        """
        # Given
        fake_plots_collection.plots[0].chart_type = ChartTypes.bar.value
        charts_interface = ChartsInterface(
            chart_plots=fake_plots_collection,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_output = charts_interface.generate_chart_output()

        # Then
        spy_generate_bar_chart.assert_called_once_with(
            plots_data=mocked_build_chart_plots_data.return_value
        )
        chart_output = ChartOutput(
            figure=spy_generate_bar_chart.return_value,
            description=charts_interface.build_chart_description(plots_data=[]),
        )
        assert generated_chart_output == chart_output

    @mock.patch.object(ChartsInterface, "build_chart_plots_data")
    @mock.patch.object(ChartsInterface, "generate_line_multi_coloured_chart")
    def test_generate_chart_figure_delegates_call_for_line_multi_coloured(
        self,
        spy_generate_line_multi_coloured_chart_method: mock.MagicMock,
        mocked_build_chart_plots_data: mock.MagicMock,
        fake_plots_collection: PlotsCollection,
    ):
        """
        Given a requirement for a `line_multi_coloured` chart
        When `generate_chart_output()` is called from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_line_multi_coloured_chart()` method

        Patches:
            `spy_generate_line_multi_coloured_chart_method`: For the
                main assertion.
            `mocked_build_chart_plots_data`: To remove the side effect
                of having to query the database for data relating to the chart

        """
        # Given
        fake_plots_collection.plots[0].chart_type = ChartTypes.line_multi_coloured.value
        charts_interface = ChartsInterface(
            chart_plots=fake_plots_collection,
            core_time_series_manager=mock.Mock(),
        )

        # When
        generated_chart_output: ChartOutput = charts_interface.generate_chart_output()

        # Then
        spy_generate_line_multi_coloured_chart_method.assert_called_once_with(
            plots_data=mocked_build_chart_plots_data.return_value
        )
        assert (
            generated_chart_output.figure
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
        plots_data = charts_interface.build_chart_plots_data()

        # When
        line_multi_coloured_chart = charts_interface.generate_line_multi_coloured_chart(
            plots_data=plots_data
        )

        # Then
        spy_line_multi_coloured_generate_chart_figure.assert_called_once_with(
            chart_height=plots_collection.chart_height,
            chart_width=plots_collection.chart_width,
            chart_plots_data=plots_data,
        )
        assert (
            line_multi_coloured_chart
            == spy_line_multi_coloured_generate_chart_figure.return_value
        )

    @mock.patch.object(ChartsInterface, "_set_latest_date_from_plots_data")
    @mock.patch(f"{MODULE_PATH}.line_with_shaded_section.generate_chart_figure")
    def test_generate_line_with_shaded_section_chart(
        self,
        spy_line_with_shaded_section_generate_chart_figure: mock.MagicMock,
        mocked_set_latest_date_from_plots_data: mock.MagicMock,
        valid_plot_parameters: PlotParameters,
    ):
        """
        Given a valid `PlotParameters` for a `line_with_shaded_section` chart
        When `generate_line_with_shaded_section_chart()` is called
            from an instance of the `ChartsInterface`
        Then the call is delegated to the `generate_chart_figure()`
            from the `line_with_shaded_section` module with the correct args

        Patches:
            `spy_line_with_shaded_section_generate_chart_figure`: For the
                main assertion.
            `mocked_set_latest_date_from_plots_data`: To isolate
                date conversion logic away from the scope of the test
        """
        # Given
        valid_plot_parameters.chart_type = ChartTypes.line_with_shaded_section.value
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
        plots_data = charts_interface.build_chart_plots_data()

        # When
        line_with_shaded_section_chart = (
            charts_interface.generate_line_with_shaded_section_chart(
                plots_data=plots_data
            )
        )

        # Then
        expected_params = charts_interface.param_builder_for_line_with_shaded_section(
            plots_data=plots_data
        )
        spy_line_with_shaded_section_generate_chart_figure.assert_called_once_with(
            **expected_params
        )
        assert (
            line_with_shaded_section_chart
            == spy_line_with_shaded_section_generate_chart_figure.return_value
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

    def test_set_latest_date_from_plots_data_fails_silently_when_latest_date_not_provided(
        self, fake_chart_plot_parameters
    ):
        """
        Given a `PlotData` model which contains
            a `PlotParameters` model which does not declare a `latest_date`
        When `_set_latest_date_from_plots_data()` is called
            from an instance of the `ChartsInterface`
        Then the `latest_date` value is left unchanged
        """
        # Given
        plots_data = PlotsCollection(
            plots=[fake_chart_plot_parameters],
            file_format="svg",
            chart_width=1000,
            chart_height=200,
            x_axis="",
            y_axis="",
        )
        mocked_plots_data = [mock.MagicMock(latest_date=None) for _ in range(3)]

        original_latest_date_value = mock.Mock()
        charts_interface = ChartsInterface(
            chart_plots=plots_data,
            core_time_series_manager=mock.Mock(),
        )
        charts_interface._latest_date = original_latest_date_value

        # When
        charts_interface._set_latest_date_from_plots_data(plots_data=mocked_plots_data)

        # Then
        assert charts_interface._latest_date == original_latest_date_value

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
                plots_data=[fake_plot_data]
            )
        )

        # When
        metric: str = fake_plot_data.parameters.metric_name
        expected_constructed_params = {
            "plots_data": [fake_plot_data],
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
            chart_output=mock.Mock()
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
        chart_output = ChartOutput(figure=mocked_figure, description="")

        charts_interface = ChartsInterface(chart_plots=mocked_plots_collection)

        # When
        encoded_chart: dict[str, str] = charts_interface.get_encoded_chart(
            chart_output=chart_output
        )

        # Then
        assert encoded_chart["chart"] == spy_encode_figure.return_value

    @mock.patch.object(ChartsInterface, "encode_figure")
    def test_get_encoded_chart_returns_description(
        self, mocked_encode_figure: mock.MagicMock
    ):
        """
        Given a mocked figure
        When `get_encoded_chart()` is called from an instance of the `ChartsInterface`
        Then the `chart` field is populated via a call to the `encode_figure()` method

        Patches:
            `mocked_create_optimized_svg`: To remove the side effect of
                creating a svg and optimizing it

        """
        # Given
        mocked_plots_collection = mock.MagicMock()
        fake_description = "abcdef"
        chart_output = ChartOutput(figure=mock.Mock(), description=fake_description)

        charts_interface = ChartsInterface(chart_plots=mocked_plots_collection)

        # When
        encoded_chart: dict[str, str] = charts_interface.get_encoded_chart(
            chart_output=chart_output
        )

        # Then
        assert encoded_chart["alt_text"] == chart_output.description


class TestGenerateChartAsFile:
    def test_raises_error_for_invalid_topic_and_metric_selection(
        self,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a mocked `PlotsCollection` model
            which contains a plot parameters model
            for an invalid metric and topic combination
        When `generate_chart_as_file()` is called
        Then an `InvalidPlotParametersError` is raised
        """
        # Given
        fake_chart_plot_parameters.topic = "RSV"
        fake_chart_plot_parameters.metric = "COVID-19_testing_PCRcountByDay"
        mocked_plots_collection = mock.Mock()
        mocked_plots_collection.plots = [fake_chart_plot_parameters]

        # When / Then
        with pytest.raises(InvalidPlotParametersError):
            generate_chart_as_file(chart_plots=mocked_plots_collection)

    def test_raises_error_for_invalid_dates_selection(
        self,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a mocked `PlotsCollection` model
            which contains a plot parameters model
            for an invalid `date_from` and `date_to` selection
        When `generate_chart_as_file()` is called
        Then an `InvalidPlotParametersError` is raised
        """
        # Given
        fake_chart_plot_parameters.date_from = "2023-01-01"
        fake_chart_plot_parameters.date_to = "2022-12-31"
        mocked_plots_collection = mock.Mock()
        mocked_plots_collection.plots = [fake_chart_plot_parameters]

        # When / Then
        with pytest.raises(InvalidPlotParametersError):
            generate_chart_as_file(chart_plots=mocked_plots_collection)

    @mock.patch.object(ChartsInterface, "write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_output")
    def test_delegates_call_for_writing_the_chart(
        self,
        spy_generate_chart_output: mock.MagicMock,
        spy_write_figure: mock.MagicMock,
        fake_chart_plot_parameters: PlotParameters,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart_as_file()` is called
        Then `write_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_plots_collection = mock.Mock()
        mocked_plots_collection.plots = [fake_chart_plot_parameters]

        # When
        generate_chart_as_file(chart_plots=mocked_plots_collection)

        # Then
        spy_write_figure.assert_called_once_with(
            figure=spy_generate_chart_output.return_value.figure,
        )


class TestGenerateEncodedChart:
    @mock.patch.object(ChartsInterface, "get_encoded_chart")
    @mock.patch.object(ChartsInterface, "generate_chart_output")
    def test_delegates_call_for_validation(
        self,
        spy_generate_chart_output: mock.MagicMock,
        mocked_get_encoded_chart: mock.MagicMock,
        fake_plots_collection: PlotsCollection,
    ):
        """
        Given a fake `PlotsCollection` model
        When `generate_encoded_chart()` is called
        Then a call is delegated to `generate_chart_figure`
            from an instance of the `ChartsInterface`

        Patches:
            `spy_generate_chart_output`: For one of
                the main assertions
            `mocked_get_encoded_chart`: To remove the side effects
                of having to encode the chart figure
        """
        # Given
        fake_chart_plots = fake_plots_collection

        # When
        generate_encoded_chart(chart_plots=fake_chart_plots)

        # Then
        spy_generate_chart_output.assert_called_once()

    @mock.patch.object(ChartsInterface, "get_encoded_chart")
    @mock.patch.object(ChartsInterface, "generate_chart_output")
    def test_delegates_call_to_get_encoded_chart(
        self,
        mocked_generate_chart_output: mock.MagicMock,
        spy_get_encoded_chart: mock.MagicMock,
        fake_plots_collection: PlotsCollection,
    ):
        """
        Given a fake `PlotsCollection` model
        When `generate_chart_output()` is called
        Then the call is delegated to `get_encoded_chart()`
            from an instance of the `ChartsInterface`

        Patches:
            `mocked_generate_chart_output`: To set the returned figure
                so that it can be encoded more easily
                and so the return value can be
                passed to the main assertion
            `spy_get_encoded_chart`: For the main assertion
        """
        # Given
        fake_chart_plots = fake_plots_collection
        mocked_figure = mock.Mock()
        mocked_figure.to_image.return_value = "abc"
        chart_output = ChartOutput(figure=mocked_figure, description="")
        mocked_generate_chart_output.return_value = chart_output

        # When
        generate_encoded_chart(chart_plots=fake_chart_plots)

        # Then
        spy_get_encoded_chart.assert_called_once_with(chart_output=chart_output)


class TestMiscMethods:
    @pytest.mark.parametrize(
        "file_format",
        [
            "png",
            "jpg",
            "jpeg",
        ],
    )
    def test_invalid_format_passed_to_encode_figure(
        self, file_format: str, fake_plots_collection: PlotsCollection
    ):
        """
        Given the user supplies an invalid file_format to pass to encode_figure
        When `encode_figure` is called from an instance of the `ChartsInterface`
        Then an `InvalidFileFormatError` is raised
        """
        # Given
        fake_plots_collection.file_format = file_format
        charts_interface = ChartsInterface(
            chart_plots=fake_plots_collection,
            core_time_series_manager=mock.Mock(),
        )

        figure = plotly.graph_objs.Figure()

        # When / Then
        with pytest.raises(InvalidFileFormatError):
            charts_interface.encode_figure(figure=figure)
