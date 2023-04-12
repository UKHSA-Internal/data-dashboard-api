from typing import List

import plotly.graph_objects

from metrics.domain.charts.line import colour_scheme, generation

DATA_POINTS: List[int] = [1, 2, 3, 2, 2, 3, 4, 5, 5, 3, 2, 1]


class TestLineCharts:
    def test_main_layout(self):
        """
        Given a list of numbers for data points
        When `generate_chart_figure()` is called from the `line` module
        Then the figure is drawn with the expected parameters for the main background and the X & Y axis
        """
        # Given
        data_points = DATA_POINTS

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            values=data_points,
        )

        # Then
        assert len(figure.data) == 1

        # ---Main background checks---
        main_layout: plotly.graph_objects.Layout = figure.layout
        # Check that the main background colour is a plain white
        assert (
            main_layout.plot_bgcolor == colour_scheme.RGBAColours.LIGHT_GREY.stringified
        )
        assert not main_layout.showlegend

        # ---X Axis checks---
        assert not main_layout.xaxis.visible

        # ---Y Axis checks---
        assert not main_layout.yaxis.visible

    def test_main_line_plot(self):
        """
        Given a list of values
        When `generate_chart_figure()` is called from the `line` module
        Then the figure is drawn with the expected parameters for the main line
        """
        # Given
        data_points = DATA_POINTS

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            values=data_points,
        )

        # Then
        assert len(figure.data) == 1

        # ---Main line plot checks---
        main_line_plot: plotly.graph_objects.Scatter = figure.data[0]

        # The main line should be drawn as a black `spline` plot
        main_line: plotly.graph_objects.scatter.Line = main_line_plot.line
        assert main_line.color == colour_scheme.RGBAColours.BLACK.stringified
        assert main_line.shape == "spline"
        assert main_line_plot.mode is None

        # The fill colour under the plot should be a dark grey
        assert (
            main_line_plot.fillcolor == colour_scheme.RGBAColours.DARK_GREY.stringified
        )

    def test_main_line_plot_can_be_enforced_with_markers(self):
        """
        Given a list of values and a requirement to enforce markers on the plot
        When `generate_chart_figure()` is called from the `line` module
        Then the figure is drawn with the expected parameters for the main line
        And the `mode` of the line plot is set to `lines+markers`
        """
        # Given
        data_points = DATA_POINTS

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            data_points=data_points,
            enforce_markers=True,
        )

        # Then
        main_line_plot: plotly.graph_objects.Scatter = figure.data[0]
        assert main_line_plot.mode == "lines+markers"
