import datetime
from typing import List

import plotly.graph_objects

from metrics.domain.charts.line_multi_coloured import colour_scheme, generation
from metrics.domain.models import PlotParameters, PlotsData

DATES_FROM_SEP_TO_JAN: List[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 9, 19),
    datetime.date(2022, 10, 3),
    datetime.date(2022, 10, 7),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 10, 21),
    datetime.date(2022, 11, 3),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2022, 12, 26),
    datetime.date(2023, 1, 9),
]
EXAMPLE_VALUES: List[int] = [10, 22, 8, 65, 81, 76, 67, 23, 12, 45, 71]
HEIGHT = 300
WIDTH = 400


class TestLineMultiColouredCharts:
    @staticmethod
    def _setup_chart_plot_data(
        x_axis: List[datetime.date],
        y_axis: List[int],
        label: str = "",
        line_type: str = "",
        line_colour: str = "",
    ) -> PlotsData:
        plot_params = PlotParameters(
            chart_type="line_multi_coloured",
            topic="RSV",
            metric="weekly_positivity_by_age",
            stratum="0_4",
            label=label,
            line_type=line_type,
            line_colour=line_colour,
        )
        return PlotsData(parameters=plot_params, x_axis=x_axis, y_axis=y_axis)

    def test_main_plot_and_axis_properties(self):
        """
        Given a `ChartPlotData` models representing a line plot
        When `generate_chart_figure()` is called from the `line_multi_coloured` module
        Then the figure is drawn with the expected parameters for the main background and the X & Y axis
        """
        # Given
        dates = DATES_FROM_SEP_TO_JAN
        values = EXAMPLE_VALUES
        chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates, y_axis=values, label="some_label"
        )

        # When
        figure = generation.generate_chart_figure(
            chart_height=HEIGHT,
            chart_width=WIDTH,
            chart_plots_data=[chart_plots_data],
        )

        # Then
        # ---Main background checks---
        main_layout = figure.layout
        # Check that the main background colour is a plain white
        assert main_layout.paper_bgcolor == colour_scheme.RGBAColours.WHITE.stringified
        # Check that the main layout is showing the legend
        assert main_layout.showlegend

        # ---Legend checks---
        # Check that the legend is placed in the centre and above the figure
        assert main_layout.legend.orientation == "h"
        assert main_layout.legend.xanchor == "center"
        assert main_layout.legend.yanchor == "bottom"
        assert main_layout.legend.y == 1.0
        assert main_layout.legend.x == 0.5

        # Check the chart sizes are as per the specified parameters
        assert main_layout.height == HEIGHT
        assert main_layout.width == WIDTH

        # ---X Axis checks---
        x_axis = main_layout.xaxis
        # The `M1` dtick setting ensures x values within the same month do not show repeated months:
        # ___Sep___Oct___Nov___  as opposed to _Sep_Sep_Oct_Oct_Oct_Nov_Nov_
        assert x_axis.dtick == "M1"
        # The date format is in `Month Year` e.g. `May 2023`
        assert x_axis.tickformat == "%b %Y"

        assert x_axis.automargin

        # ---Y Axis checks---
        y_axis = main_layout.yaxis
        assert not y_axis.showgrid

    def test_two_plots_with_provided_labels_and_colours(self):
        """
        Given 2 `ChartPlotData` models representing 2 different line plots
        When `generate_chart_figure()` is called from the `line_multi_coloured` module
        Then the figure is drawn with the expected parameters for the line plots
        """
        # Given
        dates = DATES_FROM_SEP_TO_JAN
        values = EXAMPLE_VALUES
        first_plot_line_type = "DASH"
        first_plot_label = "0 to 4 years old"
        first_plot_colour = "RED"
        first_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values,
            label=first_plot_label,
            line_type=first_plot_line_type,
            line_colour=first_plot_colour,
        )

        dates = DATES_FROM_SEP_TO_JAN
        second_plot_line_type = "SOLID"
        second_plot_label = "15 to 44 years old"
        values = [20, 45, 62, 41, 32, 43, 45, 57, 88, 76, 9]
        second_plot_colour = "BLUE"
        second_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values,
            label=second_plot_label,
            line_type=second_plot_line_type,
            line_colour=second_plot_colour,
        )

        # When
        figure = generation.generate_chart_figure(
            chart_height=HEIGHT,
            chart_width=WIDTH,
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # There should be 2 plots on the figure, one for each of the line plots
        assert len(figure.data) == 2

        # ---First line plot checks---
        first_plot: plotly.graph_objects.Scatter = figure.data[0]
        # Check that each axis has been populated with the correct data
        assert list(first_plot.x) == first_chart_plots_data.x_axis
        assert list(first_plot.y) == first_chart_plots_data.y_axis

        # The name of the plot should match the provided custom label
        assert first_plot.name == first_plot_label

        # Check that the first plotted line is a continuous `spline`
        first_plot_line: plotly.graph_objects.scatter.Line = first_plot.line
        assert first_plot_line.shape == "spline"
        assert first_plot_line.width == 2

        # Check that the first plotted line has the line type set correctly
        # Note: plotly expects this parameter lower-cased
        assert first_plot_line.dash == first_plot_line_type.lower()

        # Check that the first plotted line has been set with the correct colour
        expected_rgba_for_first_plot = colour_scheme.RGBAColours[first_plot_colour]
        assert first_plot_line.color == expected_rgba_for_first_plot.stringified

        # ---Second line plot checks---
        second_plot: plotly.graph_objects.Scatter = figure.data[1]
        # Check that each axis has been populated with the correct data
        assert list(second_plot.x) == second_chart_plots_data.x_axis
        assert list(second_plot.y) == second_chart_plots_data.y_axis

        # The name of the plot should match the provided custom label
        assert second_plot.name == second_plot_label

        # Check that the second plotted line is a continuous `spline`
        second_plot_line: plotly.graph_objects.scatter.Line = second_plot.line
        assert second_plot_line.shape == "spline"
        assert second_plot_line.width == 2

        # Check that the first plotted line has the line type set correctly
        # Note: plotly expects this parameter lower-cased
        assert second_plot_line.dash == second_plot_line_type.lower()

        # Check that the second plotted line has been set with the correct colour
        expected_rgba_for_second_plot = colour_scheme.RGBAColours[second_plot_colour]
        assert second_plot_line.color == expected_rgba_for_second_plot.stringified
