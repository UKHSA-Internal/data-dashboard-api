from datetime import date
from typing import Any, List

import plotly.graph_objects

from metrics.domain.charts.bar import colour_scheme, type_hints

TICK_FONT = type_hints.AXIS_ARGS = {
    "family": "Arial",
    "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
}

X_AXIS_TEXT_TYPE = {
    "xaxis": {
        "type": "-",
    }
}

X_AXIS_DATE_TYPE = {
    "xaxis": {
        "type": "date",
        "dtick": "M1",
        "tickformat": "%b %Y",
    }
}


X_AXIS_ARGS: type_hints.AXIS_ARGS = {
    "showgrid": False,
    "zeroline": False,
    "showline": False,
    "ticks": "outside",
    "tickson": "boundaries",
    "tickfont": TICK_FONT,
}

Y_AXIS_ARGS: type_hints.AXIS_ARGS = {
    "showgrid": False,
    "showticklabels": True,
    "tickfont": TICK_FONT,
}

BAR_CHART_LAYOUT_ARGS: type_hints.LAYOUT_ARGS = {
    "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "margin": {
        "l": 10,
        "r": 0,
        "b": 0,
        "t": 0,
    },
    "showlegend": True,
    "barmode": "group",
    "legend": {
        "orientation": "h",
        "y": -0.15,
        "x": 0,
    },
    "autosize": False,
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
}


def generate_chart_figure(
    chart_height: int,
    chart_width: int,
    x_axis_values: List[Any],
    y_axis_values: List[Any],
    legend: str,
    bar_colour: str = colour_scheme.RGBAColours.PLOT_1_BLUE.stringified,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `dates` & `values` as a Bar graph.

    Args:
        x_axis_values: The values for the x-axis
        y_axis_values: The values for the y-axis
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        dates: List of datetime objects for each of the values.
        values: List of numbers representing the values.
        legend: Legend associated with the given plot
        bar_colour: The colour to assign to the bar.
            Defaults to 86, 148, 202, 1, blue.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown
    """

    figure = plotly.graph_objects.Figure()

    # Create Bar plot
    bar_plot: plotly.graph_objects.Bar = _create_bar_plot(
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        bar_colour=bar_colour,
        legend=legend,
    )

    # Add plot to graph
    figure.add_trace(trace=bar_plot)

    # Set the height and width of the chart itself
    figure.update_layout(
        {
            "height": chart_height,
            "width": chart_width,
        }
    )

    # Set x axis tick type depending on what sort of data we are showing
    if type(x_axis_values[0]) is date:
        figure.update_layout(**X_AXIS_DATE_TYPE)
    else:
        figure.update_layout(**X_AXIS_TEXT_TYPE)

    # Apply the typical stylings for bar charts
    figure.update_layout(**BAR_CHART_LAYOUT_ARGS)

    return figure


def _create_bar_plot(
    x_axis_values: List[Any],
    y_axis_values: List[Any],
    bar_colour: str,
    legend: str,
    showlegend: bool = False,
) -> plotly.graph_objects.Bar:
    """Create a Bar plot to add to the chart (via the add_trace method)

    Args:
        x_axis_values: The values for the x-axis
        y_axis_values: The values for the y-axis
        dates: List of datetime objects for each of the values.
        values: List of numbers representing the values for this plot.
        bar_colour: The colour to assign to the bars.
        legend: Legend to display for this plot.
        showlegend: Whether or not to display the associated legend for this plot
            Note: showlegend in BAR_CHART_LAYOUT_ARGS constant has to be True
            for this setting to have any effect
    Returns:
        `Bar`: A `plotly` bar which can then be added to the chart
    """

    return plotly.graph_objects.Bar(
        x=x_axis_values,
        y=y_axis_values,
        marker={
            "color": bar_colour,
            "line": {"color": bar_colour, "width": 1},
        },
        name=legend,
        showlegend=showlegend,
    )
