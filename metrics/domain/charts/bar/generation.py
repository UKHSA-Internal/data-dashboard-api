from typing import Any

import plotly.graph_objects

from metrics.domain.charts import chart_settings, colour_scheme
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotData


def generate_chart_figure(
    chart_height: int,
    chart_width: int,
    chart_plots_data: list[PlotData],
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `dates` & `values` as a Bar graph.

    Args:
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        chart_plots_data: List of `PlotData` models,
            where each model represents a requested plot.
            Note that each `PlotData` model is enriched
            with the according x and y values along with
            requests parameters like colour and plot label.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown

    """
    figure = plotly.graph_objects.Figure()

    for plot_data in chart_plots_data:
        selected_colour: colour_scheme.RGBAChartLineColours = (
            colour_scheme.RGBAChartLineColours.get_bar_colour(
                colour=plot_data.parameters.line_colour
            )
        )

        plot_label: str = plot_data.parameters.label

        # Create Bar plot
        bar_plot: dict = _create_bar_plot(
            x_axis_values=plot_data.x_axis_values,
            y_axis_values=plot_data.y_axis_values,
            bar_colour=selected_colour.stringified,
            legend=plot_label,
            showlegend=bool(plot_label),
        )

        # Add plot to graph
        figure.add_trace(trace=bar_plot)

    settings = chart_settings.ChartSettings(
        width=chart_width, height=chart_height, plots_data=chart_plots_data
    )

    layout_args = settings.get_bar_chart_config()
    figure.update_layout(**layout_args)

    return figure


def _create_bar_plot(
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    bar_colour: str,
    legend: str,
    showlegend: bool = False,
) -> dict:
    """Create a Bar plot to add to the chart (via the add_trace method)

    Args:
        x_axis_values: The values to display along the x-axis
        y_axis_values: The values to display along the y-axis
        bar_colour: The colour to assign to the bars.
        legend: Legend to display for this plot.
        showlegend: Whether to display the associated legend for this plot
            Note: showlegend in BAR_CHART_LAYOUT_ARGS constant has to be True
            for this setting to have any effect

    Returns:
        Dictionary representation of the graph object
        which can be added to the figure

    """
    bar = plotly.graph_objects.Bar(
        x=x_axis_values,
        y=y_axis_values,
        marker={
            "color": bar_colour,
            "line": {
                "color": bar_colour,
                "width": 1,
            },
        },
        name=legend,
        showlegend=showlegend,
    )
    return convert_graph_object_to_dict(graph_object=bar)
