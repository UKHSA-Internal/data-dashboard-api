import datetime
import plotly.graph_objects
from unittest import mock

from metrics.domain.models import SubplotChartGenerationPayload
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.domain.charts.subplots.generation import generate_chart_figure
from metrics.interfaces.charts.subplot_charts.access import (
    ChartOutput,
    SubplotChartsInterface,
    generate_chart_file,
)
from metrics.interfaces.plots.access import PlotsInterface

MODULE_PATH = "metrics.interfaces.charts.subplot_charts.access"


class TestChartsInterface:
    @mock.patch(f"{MODULE_PATH}.generate_chart_figure")
    def test_build_chart_figure_delegates_call_to_generate_chart_figure(
        self,
        mock_generate_chart_figure: mock.MagicMock,
        fake_subplot_chart_generation_payload,
        fake_subplot_chart_request_params,
    ):
        """
        Given a valid `chart_generation_payload`
        When `_build_chart_figure` is called
        Then a call is made to `generate_chart_figure` with the `chart_generation_payload`
        """
        # Given
        charts_interface = SubplotChartsInterface(
            chart_request_params=fake_subplot_chart_request_params,
        )

        # When
        charts_interface._build_chart_figure(
            chart_generation_payload=fake_subplot_chart_generation_payload,
        )

        # Then
        mock_generate_chart_figure.assert_called_once_with(
            chart_generation_payload=fake_subplot_chart_generation_payload,
        )

    @mock.patch.object(PlotsInterface, "build_plots_data")
    def test_build_plots_data_delegates_call_to_plots_interface_correctly(
        self,
        spy_build_plots_data: mock.MagicMock,
        fake_subplot_chart_request_params,
    ):
        """
        Given a valid `chart_request_params`
        When `_build_plots_data` is called
        Then a call is made to `PlotsInterface.build_plots_data` for each `subplots_data` model
        """
        # Given
        charts_interface = SubplotChartsInterface(
            chart_request_params=fake_subplot_chart_request_params
        )

        # When
        charts_interface._build_plots_data()

        # Then
        assert spy_build_plots_data.call_count == len(
            fake_subplot_chart_request_params.subplots
        )

    @mock.patch.object(SubplotChartsInterface, "_build_plots_data")
    def test_build_chart_generation_payload_delegates_call_to_build_plots_data(
        self,
        spy_build_plots_data: mock.MagicMock,
        fake_subplot_chart_request_params: SubplotChartGenerationPayload,
    ):
        """
        Given a valid `SubplotChartRequestParameters` model
        When `_build_chart_generation_payload` is called
        Then the a call is made to `_build_plots_data()`
        """
        # Given
        charts_interface = SubplotChartsInterface(
            chart_request_params=fake_subplot_chart_request_params,
        )

        # When
        charts_interface._build_chart_generation_payload()

        # Then
        spy_build_plots_data.assert_called_once()

    @mock.patch.object(SubplotChartsInterface, "_build_chart_generation_payload")
    @mock.patch.object(SubplotChartsInterface, "_build_chart_figure")
    def test_generate_chart_output_returns_instance_of_chart_output(
        self,
        mock_build_chart_figure: mock.MagicMock,
        mock_build_chart_generation_payload: mock.MagicMock,
        fake_subplot_chart_request_params,
    ):
        """
        Given a valid `chart_request_params` model
        When `generate_chart_output` is called
        Then an instance of `ChartOutput` model is returned
        """
        # Given
        charts_interface = SubplotChartsInterface(
            chart_request_params=fake_subplot_chart_request_params
        )

        # When
        chart_output = charts_interface.generate_chart_output()

        # Then
        assert isinstance(chart_output, ChartOutput)
        assert chart_output.figure == mock_build_chart_figure.return_value

    def test_write_figure_as_bytes(
        self,
        fake_subplot_chart_request_params,
    ):
        """
        Given a valid `figure` plotly object
        When `write_figure` is called
        Then a bytes object is returned
        """
        # Given
        charts_interface = SubplotChartsInterface(
            chart_request_params=fake_subplot_chart_request_params
        )
        fake_figure = plotly.graph_objects.Figure()

        # When
        chart_bytes = charts_interface.write_figure(figure=fake_figure)

        # Then
        assert type(chart_bytes) == bytes


class TestGenerateChartAsFile:
    @mock.patch.object(SubplotChartsInterface, "generate_chart_output")
    @mock.patch.object(SubplotChartsInterface, "write_figure")
    def test_delegates_call_for_writing_chart(
        self,
        spy_write_figure: mock.MagicMock,
        spy_generate_chart_output: mock.MagicMock,
        fake_subplot_chart_request_params: SubplotChartGenerationPayload,
    ):
        """
        Given a mock in place of a `SubplotChartGenerationPayload` model
        When `generate_chart_as_file` is called
        Then `write_figure` is called from an instance of the `ChartsInterface`
        """
        # Given
        mocked_subplot_collection = mock.Mock()
        mocked_subplot_collection.subplots_data = fake_subplot_chart_request_params

        # When
        generate_chart_file(chart_request_params=mocked_subplot_collection)

        # Then
        spy_write_figure.assert_called_once_with(
            figure=spy_generate_chart_output.return_value.figure,
        )
