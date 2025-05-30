import datetime
from typing import Any

import plotly.graph_objects

from metrics.domain.charts.colour_scheme import RGBAChartLineColours, RGBAColours

from metrics.domain.charts.common_charts import generation
from metrics.domain.models import (
    PlotGenerationData,
    PlotParameters,
    ChartGenerationPayload,
)

DATES_FROM_SEP_TO_JAN: list[datetime.datetime] = [
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
EXAMPLE_VALUES: list[int] = [10, 22, 8, 65, 81, 76, 67, 23, 12, 45, 71]
HEIGHT = 220
WIDTH = 930


class TestLineMultiColouredCharts:
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
            metric="COVID-19_deaths_ONSByDay",
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

    def test_main_plot_and_axis_properties(self):
        """
        Given a `PlotData` model representing a line plot
        When `generate_chart_figure()` is called from the `line_multi_coloured` module
        Then the figure is drawn with the expected parameters for the main background and the X & Y axis
        """
        # Given
        x_axis_values = DATES_FROM_SEP_TO_JAN
        y_axis_values = EXAMPLE_VALUES
        chart_plots_data = self._setup_chart_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            label="some_label",
        )
        payload = ChartGenerationPayload(
            chart_height=HEIGHT,
            chart_width=WIDTH,
            plots=[chart_plots_data],
            x_axis_title="",
            y_axis_title="",
        )

        # When
        figure = generation.generate_chart_figure(chart_generation_payload=payload)

        # Then
        # ---Main background checks---
        main_layout = figure.layout
        # Check that the main background colour is a plain white
        assert main_layout.paper_bgcolor == RGBAColours.WHITE.stringified
        # Check that the main layout is showing the legend
        assert main_layout.showlegend

        # Check left and right margins are both 0
        assert figure.layout.margin.l == figure.layout.margin.r == 0

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

        # ---Y Axis checks---
        y_axis = main_layout.yaxis
        assert not y_axis.showgrid

    def test_x_axis_type_is_not_date(self):
        """
        Given a list of x and y values where x values are NOT dates
        When `generate_chart_figure()` is called from the `line_multi_coloured` module
        Then the figure is drawn with the expected parameters for the x axis
        """
        # Given
        x_axis_values = ["0-4", "5-8", "9-29"]
        y_axis_values = EXAMPLE_VALUES
        chart_plots_data = self._setup_chart_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            label="some_label",
        )
        payload = ChartGenerationPayload(
            chart_height=HEIGHT,
            chart_width=WIDTH,
            plots=[chart_plots_data],
            x_axis_title="",
            y_axis_title="",
        )

        # When
        figure = generation.generate_chart_figure(chart_generation_payload=payload)

        # Then

        # Check left and right margins are both 0
        assert figure.layout.margin.l == 0
        assert figure.layout.margin.r == 0

        # ---X Axis checks---
        x_axis = figure.layout.xaxis

        # The `M1` dtick setting is only valid for dates
        assert x_axis.dtick is None

        # The x-axis type and ticks should be the default
        assert x_axis.type == "-"
        assert x_axis.tickformat is None

        # ---Y Axis checks---
        y_axis = figure.layout.yaxis

        # Labels should be shown for y-axis ticks
        assert y_axis.showticklabels

    def test_two_plots_with_provided_labels_and_colours(self):
        """
        Given 2 `PlotData` models representing 2 different line plots
        When `generate_chart_figure()` is called from the `line_multi_coloured` module
        Then the figure is drawn with the expected parameters for the line plots
        """
        # Given
        x_axis_values = DATES_FROM_SEP_TO_JAN
        y_axis_values = EXAMPLE_VALUES
        first_plot_line_type = "DASH"
        first_plot_label = "0 to 4 years old"
        first_plot_colour = "RED"
        first_chart_plots_data = self._setup_chart_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            label=first_plot_label,
            line_type=first_plot_line_type,
            line_colour=first_plot_colour,
            use_markers=True,
        )

        x_axis_values = DATES_FROM_SEP_TO_JAN
        x_axis_values_as_strings = [str(x) for x in x_axis_values]
        y_axis_values = [20, 45, 62, 41, 32, 43, 45, 57, 88, 76, 9]
        second_plot_line_type = "SOLID"
        second_plot_label = "15 to 44 years old"
        second_plot_colour = "BLUE"
        second_chart_plots_data = self._setup_chart_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            label=second_plot_label,
            line_type=second_plot_line_type,
            line_colour=second_plot_colour,
            use_smooth_lines=False,
        )
        payload = ChartGenerationPayload(
            chart_height=HEIGHT,
            chart_width=WIDTH,
            plots=[first_chart_plots_data, second_chart_plots_data],
            x_axis_title="",
            y_axis_title="",
        )

        # When
        figure = generation.generate_chart_figure(chart_generation_payload=payload)

        # Then
        # There should be 2 plots on the figure, one for each of the line plots
        assert len(figure.data) == 2

        # ---First line plot checks---
        first_plot: plotly.graph_objects.Scatter = figure.data[0]
        # Check that each axis has been populated with the correct data
        # Note that the dates along the x-axis are returned as strings
        # i.e. `2022-9-5` instead of as datetime objects hence the need for the string conversion
        assert list(first_plot.x) == x_axis_values_as_strings
        assert list(first_plot.y) == first_chart_plots_data.y_axis_values
        # Check that the `use_markers` boolean is applied correctly
        assert first_plot.mode == "lines+markers"

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
        expected_rgba_for_first_plot = RGBAChartLineColours[first_plot_colour]
        assert first_plot_line.color == expected_rgba_for_first_plot.stringified

        # ---Second line plot checks---
        second_plot: plotly.graph_objects.Scatter = figure.data[1]
        # Check that each axis has been populated with the correct data
        assert list(second_plot.x) == x_axis_values_as_strings
        assert list(second_plot.y) == second_chart_plots_data.y_axis_values

        assert second_plot.mode == "lines"

        # The name of the plot should match the provided custom label
        assert second_plot.name == second_plot_label

        # Check that the second plotted line is a `linear` plot
        second_plot_line: plotly.graph_objects.scatter.Line = second_plot.line
        assert second_plot_line.shape == "linear"
        assert second_plot_line.width == 2

        # Check that the first plotted line has the line type set correctly
        # Note: plotly expects this parameter lower-cased
        assert second_plot_line.dash == second_plot_line_type.lower()

        # Check that the second plotted line has been set with the correct colour
        expected_rgba_for_second_plot = RGBAChartLineColours[second_plot_colour]
        assert second_plot_line.color == expected_rgba_for_second_plot.stringified
