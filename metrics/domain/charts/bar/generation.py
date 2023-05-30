from datetime import datetime
from typing import List, Union

import plotly.graph_objects

from metrics.domain.charts import chart_settings, colour_scheme, type_hints

BAR_CHART_LAYOUT_ARGS: type_hints.CHART_ARGS = chart_settings.CHART_SETTINGS | {
    "showlegend": True,
    "barmode": "group",
    "legend": {
        "orientation": "h",
        "y": -0.15,
        "x": 0,
    },
}


def generate_chart_figure(
    chart_height: int,
    chart_width: int,
    dates: List[datetime],
    values: List[Union[int, float]],
    legend: str,
    bar_colour: str = colour_scheme.RGBAColours.BAR_PLOT_1_BLUE.stringified,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `dates` & `values` as a Bar graph.

    Args:
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
        dates=dates,
        values=values,
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

    # Apply the typical stylings for bar charts
    figure.update_layout(**BAR_CHART_LAYOUT_ARGS)

    # We want to see tick labels on the Y Axis
    figure.update_yaxes(showticklabels=True)

    return figure


def _create_bar_plot(
    dates: List[datetime],
    values: List[Union[int, float]],
    bar_colour: str,
    legend: str,
    showlegend: bool = False,
) -> plotly.graph_objects.Bar:
    """Create a Bar plot to add to the chart (via the add_trace method)

    Args:
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
        x=dates,
        y=values,
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
