import datetime
from typing import List

import plotly

from metrics.domain.charts import type_hints
from metrics.domain.charts.line_with_shaded_section import colour_scheme, information

X_AXIS_ARGS: type_hints.AXIS_ARGS = {
    "showgrid": False,
    "zeroline": False,
    "showline": False,
    "ticks": "outside",
    "tickson": "boundaries",
    "type": "date",
    "tickformat": "%b",
    "tickfont": {
        "family": '"GDS Transport", Arial, sans-serif',
        "size": 20,
        "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
    },
}

Y_AXIS_ARGS: type_hints.AXIS_ARGS = {
    "showgrid": False,
    "showticklabels": False,
}

TIMESERIES_LAYOUT_ARGS: type_hints.LAYOUT_ARGS = {
    "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "margin": {
        "l": 0,
        "r": 0,
        "b": 4,
        "t": 0,
    },
    "showlegend": False,
    "height": 350,
    "autosize": False,
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
}


def create_line_chart_with_highlighted_section(
    dates: List[datetime.datetime],
    values: List[int],
    highlighted_section_fill_colour: colour_scheme.RGBAColours,
    highlighted_section_line_colour: colour_scheme.RGBAColours,
    rolling_period_slice: int,
    line_shape: str,
    line_width: int = 2,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        dates: List of datetime objects for each of the values.
        values: List of numbers representing the values.
        highlighted_section_fill_colour: The colour to use
            for the fill of the highlighted section.
        highlighted_section_line_colour: The colour to use
            for the line of the highlighted section.
        rolling_period_slice: The last N number of items to slice
            off the given `values` and show a highlighted section for.
            Note that this highlighted section will be green or red,
            depending on the average of the sliced section and
            the `metric_name`.
        line_shape: The shape to assign to the line plots.
            This can be either `linear` or `spline`.
        line_width: The weight to assign to the width of the line plots.
            Defaults to 2.
    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    # Calculate the index to perform the slices with
    preceding_data_points_count = len(values) - (rolling_period_slice + 1)

    figure = plotly.graph_objects.Figure()

    # Create the line plot for the preceding points as a simple neutral grey line
    line_plot = plotly.graph_objects.Scatter(
        x=dates[: preceding_data_points_count + 1],
        y=values[: preceding_data_points_count + 1],
        line={
            "width": line_width,
            "color": colour_scheme.RGBAColours.DARK_GREY.stringified,
        },
        line_shape=line_shape,
    )

    # Add line plot to the figure
    figure.add_trace(trace=line_plot)

    # Create the highlighted section for the last `n` points
    # Where `n` is denoted by `rolling_period_slice`
    highlighted_section_plot = plotly.graph_objects.Scatter(
        x=dates[preceding_data_points_count:],
        y=values[preceding_data_points_count:],
        line={"width": line_width},
        mode="lines",
        fill="tozeroy",
        hoveron="points",
        opacity=0.5,
        line_color=highlighted_section_line_colour.stringified,
        fillcolor=highlighted_section_fill_colour.stringified,
        line_shape=line_shape,
    )

    # Add the highlighted section plot to the figure
    figure.add_trace(trace=highlighted_section_plot)

    # Apply the typical stylings for timeseries charts
    figure.update_layout(**TIMESERIES_LAYOUT_ARGS)

    return figure


def generate_chart_figure(
    dates: List[datetime.datetime],
    values: List[int],
    metric_name: str,
    rolling_period_slice: int = 7,
    line_shape: str = "spline",
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        dates: List of datetime objects for each of the values.
        values: List of numbers representing the values.
        metric_name: The associated metric_name,
            E.g. new_admissions_daily
        rolling_period_slice: The last N number of items to slice
            off the given `values` and show a highlighted section for.
            Note that this highlighted section will be green or red,
            depending on the average of the sliced section and
            the `metric_name`.
            Defaults to 7.
        line_shape: The shape to assign to the line plots.
            Defaults to "spline", a curved shape between points.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    Raises:
        `ValueError`: If the metric_name is not supported.

    """
    line_colour, fill_colour = information.determine_line_and_fill_colours(
        values=values,
        metric_name=metric_name,
        last_n_values_to_analyse=rolling_period_slice,
    )

    return create_line_chart_with_highlighted_section(
        dates=dates,
        values=values,
        rolling_period_slice=rolling_period_slice,
        line_shape=line_shape,
        highlighted_section_line_colour=line_colour,
        highlighted_section_fill_colour=fill_colour,
    )
