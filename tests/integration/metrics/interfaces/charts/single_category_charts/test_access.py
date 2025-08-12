from unittest import mock
from typing import Any

import plotly

from metrics.domain.models import (
    ChartRequestParams,
    PlotGenerationData,
    PlotParameters,
    ChartGenerationPayload,
)

from metrics.domain.charts.common_charts import generation as common_chart_generation
from metrics.domain.common.utils import ChartTypes
from metrics.interfaces.charts.single_category_charts.access import (
    ChartsInterface,
)
from metrics.interfaces.charts.common.chart_output import ChartOutput


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


class TestChartsOutput:
    @staticmethod
    def _setup_chart_plot_data(
        x_axis_values: list[Any],
        y_axis_values: list[Any],
        label: str = "",
        line_type: str = "",
        line_colour: str = "",
        use_markers: bool = False,
        use_smooth_lines: bool = True,
    ) -> PlotGenerationData:
        plot_params = PlotParameters(
            chart_type="line_multi_coloured",
            topic="COVID-19",
            metric="COVID-19_cases_casesByDay",
            stratum="default",
            label=label,
            line_type=line_type,
            line_colour=line_colour,
            use_markers=use_markers,
            use_smooth_lines=use_smooth_lines,
        )
        return PlotGenerationData(
            parameters=plot_params,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
        )

    def test_chart_output_returns_correct_hovertemplates_for_timeseries(self):
        """ "
        Given A valid Plotly `Figure`
        When `ChartOutput` is passed the figure and `is_headline = False`
        Then a `hovertemplate` for timeseries charts is returned.
        """
        # Given
        x_axis_values = ["2025-01-01", "2025-02-01", "2025-03-01"]
        y_axis_values = [1, 2, 3]
        chart_plots_data = self._setup_chart_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            label="plot label",
        )
        payload = ChartGenerationPayload(
            chart_height="400",
            chart_width="600",
            plots=[chart_plots_data],
            x_axis_title="",
            y_axis_title="",
        )

        figure = common_chart_generation.generate_chart_figure(
            chart_generation_payload=payload
        )

        # When
        chart_output = ChartOutput(
            figure=figure,
            description="test chart",
            is_headline=False,
        ).interactive_chart_figure_output

        expected_hover_template = "%{y:,} (%{x|%d %b %Y})<extra></extra>"

        # Then
        assert chart_output["data"][0]["hovertemplate"] == expected_hover_template

    def test_chart_output_retuns_correct_hovertemplates_for_headline(self):
        """ "
        Given A valid Plotly `Figure`
        When `ChartOutput` is passed the figure and `is_headline = True`
        Then a `hovertemplate` for headline charts is returned.
        """
        # Given
        x_axis_values = ["00-01", "04-15", "35+"]
        y_axis_values = [1, 2, 3]
        chart_plots_data = self._setup_chart_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            label="plot label",
        )
        payload = ChartGenerationPayload(
            chart_height="400",
            chart_width="600",
            plots=[chart_plots_data],
            x_axis_title="",
            y_axis_title="",
        )

        figure = common_chart_generation.generate_chart_figure(
            chart_generation_payload=payload
        )

        # When
        chart_output = ChartOutput(
            figure=figure,
            description="test chart",
            is_headline=True,
        ).interactive_chart_figure_output

        expected_hover_template = "%{y:,} (%{x})<extra></extra>"

        # Then
        assert chart_output["data"][0]["hovertemplate"] == expected_hover_template
