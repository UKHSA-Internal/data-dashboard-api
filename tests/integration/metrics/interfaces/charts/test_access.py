from unittest import mock

import plotly

from metrics.domain.models import ChartRequestParams
from metrics.domain.common.utils import ChartTypes
from metrics.interfaces.charts.access import ChartsInterface


class TestChartsInterface:
    def test_svg_passed_to_encode_figure(
        self, fake_chart_request_params: ChartRequestParams
    ):
        """
        Given the user supplies a file_format of `svg` to pass to encode_figure
        When `encode_figure` is called then no exception is raised as long as
        the format is supported by the Plotly `to_image` function
        """
        # Given
        fake_chart_request_params.file_format = "svg"
        fake_chart_request_params.plots[0].chart_type = (
            ChartTypes.line_multi_coloured.value
        )
        charts_interface = ChartsInterface(
            chart_request_params=fake_chart_request_params,
        )

        figure = plotly.graph_objs.Figure()

        # When
        encoded_figure = charts_interface.encode_figure(figure=figure)

        # Then
        assert isinstance(encoded_figure, str)

    @mock.patch("scour.scour.scourString")
    def test_scour_is_called(
        self,
        mocked_scourstring: mock.MagicMock,
        fake_chart_request_params: ChartRequestParams,
    ):
        """
        Given a Plotly Figure
        When `create_optimized_svg()` is called from an instance of the `ChartsInterface`
        And the format is svg
        Then `scour.scourString` from the scour library is called
        """

        # Given
        fake_chart_request_params.file_format = "svg"
        fake_chart_request_params.plots[0].chart_type = (
            ChartTypes.line_multi_coloured.value
        )
        charts_interface = ChartsInterface(
            chart_request_params=fake_chart_request_params,
        )

        figure = plotly.graph_objs.Figure()

        # When
        figure_image = charts_interface.create_optimized_svg(figure=figure)

        # Then
        mocked_scourstring.assert_called_once()
        assert mocked_scourstring.return_value == figure_image
