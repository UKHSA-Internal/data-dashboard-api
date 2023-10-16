from unittest import mock

import plotly

from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import ChartsInterface


class TestChartsInterface:
    def test_svg_passed_to_encode_figure(self):
        """
        Given the user supplies a file_format of `svg` to pass to encode_figure
        When `encode_figure` is called then no exception is raised as long as
        the format is supported by the Plotly `to_image` function
        """
        # Given
        mocked_chart_plot_params = mock.Mock(chart_type=ChartTypes.simple_line.value)
        mocked_chart_plots = mock.Mock(
            file_format="svg",
            plots=[mocked_chart_plot_params],
        )

        charts_interface = ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

        figure = plotly.graph_objs.Figure()

        # When
        encoded_figure = charts_interface.encode_figure(figure=figure)

        # Then
        assert isinstance(encoded_figure, str)

    @mock.patch("scour.scour.scourString")
    def test_scour_is_called(self, mocked_scourstring: mock.MagicMock):
        """
        Given a Plotly Figure
        When `create_optimized_svg()` is called from an instance of the `ChartsInterface`
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
        figure_image = charts_interface.create_optimized_svg(figure=figure)

        # Then
        mocked_scourstring.assert_called_once()
        assert mocked_scourstring.return_value == figure_image
