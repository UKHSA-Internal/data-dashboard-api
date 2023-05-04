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
        "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
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
}


def get_available_colour_and_line_combos():
    available_plot_colours = colour_scheme.RGBAColours.available_plot_colours()
    combos = []
    for index, colour in enumerate(available_plot_colours):
        if index < 3:
            dash = "solid"
        else:
            dash = "dot"

        combos.append({"colour": colour, "dash": dash})

    return combos


def create_multi_coloured_line_chart(
    chart_plots_data: List[ChartPlotData],
    line_shape: str,
    line_width: int = 2,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        chart_plots_data: List of numbers representing the values.
        line_shape: The shape to assign to the line plots.
            This can be either `linear` or `spline`.
        line_width: The weight to assign to the width of the line plots.
            Defaults to 2.
    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    figure = plotly.graph_objects.Figure()

    # Create the line plot for the preceding points as a simple neutral grey line
    available_combos = get_available_colour_and_line_combos()

    for index, plot_data in enumerate(chart_plots_data):
        label = get_label_from_plot_data(plot_data=plot_data)
        dates, values = plot_data.data
        combo = available_combos[index]
        selected_colour: colour_scheme.RGBAColours = combo["colour"]

        line_plot: plotly.graph_objects.Scatter = _create_line_plot(
            dates=dates,
            values=values,
            colour=selected_colour.stringified,
            line_width=line_width,
            line_shape=line_shape,
            legend=label,
            dash=combo["dash"],
        )

        # Add line plot to the figure
        figure.add_trace(trace=line_plot)

    # Apply the typical stylings for timeseries charts
    figure.update_layout(**LAYOUT_ARGS)

    return figure


def _create_line_plot(
    dates: List[datetime.datetime],
    values: List[int],
    colour: str,
    line_width: int,
    line_shape: str,
    legend: str,
    dash: str,
):
    return plotly.graph_objects.Scatter(
        x=dates,
        y=values,
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
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        chart_plots_data:
        line_shape: The shape to assign to the line plots.
            Defaults to "spline", a curved shape between points.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    return create_multi_coloured_line_chart(
        chart_plots_data=chart_plots_data,
        line_shape=line_shape,
    )
