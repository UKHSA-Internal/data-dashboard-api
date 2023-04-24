from datetime import datetime
from typing import Dict, List, Union

import plotly.graph_objects

from metrics.domain.charts.bar import colour_scheme

AXIS_ARGS = Dict[
    str,
    Union[
        bool,
        str,
        Dict[str, Union[str, int, colour_scheme.RGBAColours]],
    ],
]

LAYOUT_ARGS = Dict[
    str,
    Union[
        colour_scheme.RGBAColours,
        Dict[str, int],
        bool,
        Dict[str, Union[str, float, int]],
        str,
        int,
        AXIS_ARGS,
    ],
]

X_AXIS_ARGS: AXIS_ARGS = {
    "showgrid": False,
    "zeroline": False,
    "showline": False,
    "ticks": "outside",
    "tickson": "boundaries",
    "type": "date",
    "dtick": "M1",
    "tickformat": "%b",
    "tickfont": {
        "family": '"GDS Transport", Arial, sans-serif',
        "size": 20,
        "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
    },
}

Y_AXIS_ARGS: AXIS_ARGS = {
    "showgrid": False,
    "showticklabels": False,
}

TIMESERIES_LAYOUT_ARGS: LAYOUT_ARGS = {
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
    "height": 350,
    "autosize": False,
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
}


def generate_chart_figure(
    dates: List[datetime],
    values: List[Union[int, float]],
    legend: str,
    bar_colour=colour_scheme.RGBAColours.PLOT_1_BLUE.stringified,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `dates` & `values` as a Bar graph.

    Args:
        dates: List of datetime objects for each of the values.
        values: List of numbers representing the values.
        legend: Legend associated with the given plot
        bar_color: The color to assign to the bar.
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

    # Apply the typical stylings for bar charts
    figure.update_layout(**TIMESERIES_LAYOUT_ARGS)

    return figure


def _create_bar_plot(
    dates: List[datetime],
    values: List[Union[int, float]],
    bar_colour: str,
    legend: str,
    showlegend: bool = False,
) -> plotly.graph_objects.Bar:
    return plotly.graph_objects.Bar(
        x=dates,
        y=values,
        marker_color=bar_colour,
        name=legend,
        showlegend=showlegend,
    )
