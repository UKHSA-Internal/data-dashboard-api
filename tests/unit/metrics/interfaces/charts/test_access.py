import datetime
from typing import Dict, List
from unittest import mock

import plotly.graph_objects
import pytest

from metrics.api.serializers.charts import FILE_FORMAT_CHOICES
from metrics.domain.charts.line_multi_coloured import generation
from metrics.domain.models import PlotParameters, PlotsCollection, PlotsData
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import (
    ChartsInterface,
    generate_chart_as_file,
    generate_encoded_chart,
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

        Patches:
            `spy_line_multi_coloured_generate_chart_figure`: For the
                main assertion.
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
        fake_plot_data = PlotsData(
            parameters=fake_chart_plot_parameters,
            x_axis_values=mocked_x_axis_values,
            y_axis_values=mocked_y_axis_values,
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

    @mock.patch.object(ChartsInterface, "get_last_updated")
    def test_get_encoded_chart_delegates_call_to_get_last_updated(
        self, spy_get_last_updated: mock.MagicMock
    ):
        """
        Given a mocked figure which returns
        When `get_encoded_chart()` is called from an instance of the `ChartsInterface`
        Then the `last_updated` field is populated via a call to the `get_last_updated()` method

        Patches:
            `spy_get_last_updated`: For the main assertion
        """
        # Given
        mocked_plots_collection = mock.MagicMock()
        mocked_figure = mock.Mock()
        mocked_figure.to_image.return_value = "abc"
        charts_interface = ChartsInterface(chart_plots=mocked_plots_collection)

        # When
        encoded_chart: Dict[str, str] = charts_interface.get_encoded_chart(
            figure=mocked_figure
        )

        # Then
        assert encoded_chart["last_updated"] == spy_get_last_updated.return_value

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
        encoded_chart: Dict[str, str] = charts_interface.get_encoded_chart(
            figure=mocked_figure
        )

        # Then
        assert encoded_chart["chart"] == spy_encode_figure.return_value


class TestGenerateChartAsFile:
    @mock.patch.object(ChartsInterface, "write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_chart_plot")
    def test_delegates_call_for_validation(
        self,
        spy_validate_each_requested_chart_plot: mock.MagicMock,
        spy_generate_chart_figure: mock.MagicMock,
        mocked_write_figure: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart_as_file()` is called
        Then a call is delegated to `validate_each_requested_chart_plot()` for validation purposes
        And `generate_chart_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_chart_as_file(chart_plots=mocked_chart_plots)

        # Then
        spy_validate_each_requested_chart_plot.assert_called_once_with(
            chart_plots=mocked_chart_plots
        )
        spy_generate_chart_figure.assert_called_once_with()

    @mock.patch.object(ChartsInterface, "write_figure")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_chart_plot")
    def test_delegates_call_for_writing_the_chart(
        self,
        mocked_validate_each_requested_chart_plot: mock.MagicMock,
        spy_generate_chart_figure: mock.MagicMock,
        spy_write_figure: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_chart_as_file()` is called
        Then a call is delegated to `validate_each_requested_chart_plot()` for validation purposes
        And `write_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_chart_plots = mock.MagicMock(plots=[mock.Mock()])

        # When
        generate_chart_as_file(chart_plots=mocked_chart_plots)

        # Then
        spy_write_figure.assert_called_once_with(
            figure=spy_generate_chart_figure.return_value,
            topic="-",
        )


class TestGenerateEncodedChart:
    @mock.patch.object(ChartsInterface, "get_encoded_chart")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_chart_plot")
    def test_delegates_call_for_validation(
        self,
        spy_validate_each_requested_chart_plot: mock.MagicMock,
        spy_generate_chart_figure: mock.MagicMock,
        mocked_get_encoded_chart: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_encoded_chart()` is called
        Then a call is delegated to `validate_each_requested_chart_plot()` for validation purposes
        And `generate_chart_figure` is called from an instance of the `ChartsInterface`

        Patches:
            `spy_validate_each_requested_chart_plot`: For one of
                the main assertions
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
        spy_validate_each_requested_chart_plot.assert_called_once_with(
            chart_plots=mocked_chart_plots
        )
        spy_generate_chart_figure.assert_called_once_with()

    @mock.patch.object(ChartsInterface, "get_encoded_chart")
    @mock.patch.object(ChartsInterface, "generate_chart_figure")
    @mock.patch(f"{MODULE_PATH}.validate_each_requested_chart_plot")
    def test_delegates_call_to_get_encoded_chart(
        self,
        mocked_validate_each_requested_chart_plot: mock.MagicMock,
        mocked_generate_chart_figure: mock.MagicMock,
        spy_get_encoded_chart: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotsCollection` model
        When `generate_encoded_chart()` is called
        Then the call is delegated to `get_encoded_chart()`
            from an instance of the `ChartsInterface`

        Patches:
            `mocked_validate_each_requested_chart_plot`: To remove
                side effects of accessing the db
                for validating the requested chart
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

        Patches:
            `spy_validate_chart_plot_parameters`: For the main assertion
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

        Patches:
            `spy_validate_method`: For the main assertion
        """
        # Given
        chart_plot_parameters = fake_chart_plot_parameters

        # When
        validate_chart_plot_parameters(chart_plot_parameters=chart_plot_parameters)

        # Then
        spy_validate_method.assert_called_once()


class TestMiscMethods:
    @pytest.mark.parametrize("file_format", FILE_FORMAT_CHOICES)
    def test_valid_format_passed_to_encode_figure(self, file_format: str):
        """
        Given the user supplies a file_format to pass to encode_figure
        When `encode_figure` is called then no exception is raised as long as
        the format is supported by the Plotly `to_image` function
        Therefore any unsupported formats added to FILE_FORMAT_CHOICES in the future
        will be picked up by this test
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

        try:
            # When / Then
            charts_interface.encode_figure(figure)
        except:
            assert (
                False
            ), f"An invalid/unsupported file format of '{file_format}' was passed to encode_figure function"

    @mock.patch("scour.scour.scourString")
    def test_non_svg_is_returned_asis(self, mock_scourstring):
        """
        Given a Plotly Figure
        When `create_image_and_optimize_it()` is called from an instance of the `ChartsInterface`
        And the format is NOT svg
        Then the Plotly Figure is returned asis and the scour function is not called
        """

        # Given
        file_format = "jpg"
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

        # When
        figure_image = charts_interface.create_image_and_optimize_it(figure)

        # Then
        assert figure_image == figure.to_image(format=file_format)
        mock_scourstring.assert_not_called()

    @mock.patch("scour.scour.scourString")
    def test_scour_is_called(self, mock_scourstring):
        """
        Given a Plotly Figure
        When `create_image_and_optimize_it()` is called from an instance of the `ChartsInterface`
        And the format is svg
        Then `scour.scourString` from the scour library is called
        """

        # Given
        file_format = "svg"
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

        # When
        figure_image = charts_interface.create_image_and_optimize_it(figure)

        # Then
        mock_scourstring.assert_called_once()
        assert mock_scourstring.return_value == figure_image
