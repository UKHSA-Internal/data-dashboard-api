import datetime
from typing import List

import plotly

from metrics.domain.charts.line_multi_coloured import colour_scheme
from metrics.domain.models import ChartPlotData

X_AXIS_ARGS = {
    "showgrid": False,
    "zeroline": False,
    "showline": False,
    "ticks": "outside",
    "tickson": "boundaries",
    "type": "date",
    "dtick": "M1",
    "tickformat": "%b %Y",
    "tickfont": {
        "family": '"GDS Transport", Arial, sans-serif',
        "color": colour_scheme.RGBAColours.BLACK.stringified,
    },
}

Y_AXIS_ARGS = {
    "showgrid": False,
    "showticklabels": False,
}

LAYOUT_ARGS = {
    "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "margin": {
        "l": 0,
        "r": 0,
        "b": 0,
        "t": 0,
    },
    "showlegend": True,
    "height": 350,
    "autosize": False,
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
    "legend": {"orientation": "h", "x": 0, "y": 1},
}


def create_multi_coloured_line_chart(
    chart_plots_data: List[ChartPlotData],
    line_shape: str,
    line_width: int = 2,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_plots_data: List of `ChartPlotData` models,
            where each model represents a requested plot.
        line_shape: The shape to assign to the line plots.
            This can be either `linear` or `spline`.
        line_width: The weight to assign to the width of the line plots.
            Defaults to 2.
    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    figure = plotly.graph_objects.Figure()

    for index, plot_data in enumerate(chart_plots_data):
        selected_colour = colour_scheme.RGBAColours.get_colour(
            colour=plot_data.parameters.line_colour
        )

        line_plot: plotly.graph_objects.Scatter = _create_line_plot(
            x_axis=plot_data.x_axis,
            y_axis=plot_data.y_axis,
            colour=selected_colour.stringified,
            line_width=line_width,
            line_shape=line_shape,
            legend=plot_data.parameters.label,
        )

        # Add line plot to the figure
        figure.add_trace(trace=line_plot)

    # Apply the typical stylings for timeseries charts
    figure.update_layout(**LAYOUT_ARGS)

    return figure


def _create_line_plot(
    x_axis: List[datetime.datetime],
    y_axis: List[int],
    colour: str,
    line_width: int,
    line_shape: str,
    legend: str,
    dash: str,
):
    return plotly.graph_objects.Scatter(
        x=x_axis,
        y=y_axis,
        line={
            "width": line_width,
            "color": colour,
            "dash": dash,
        },
        line_shape=line_shape,
        name=legend,
    )


def generate_chart_figure(
    chart_plots_data: List[ChartPlotData],
    line_shape: str = "spline",
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_plots_data: List of `ChartPlotData` models,
            where each model represents a requested plot.
        line_shape: The shape to assign to the line plots.
            This can be either `linear` or `spline`.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    return create_multi_coloured_line_chart(
        chart_plots_data=chart_plots_data,
        line_shape=line_shape,
    )
