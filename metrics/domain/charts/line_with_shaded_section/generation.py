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
    "tickformat": "%e %b %Y",
    "tickfont": {
        "family": '"GDS Transport", Arial, sans-serif',
        "size": 10,
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


def create_line_chart_with_shaded_section(
    values: List[int],
    dates: List[datetime.datetime],
    shaded_section_fill_colour: colour_scheme.RGBAColours,
    shaded_section_line_colour: colour_scheme.RGBAColours,
    rolling_period_slice: int,
    line_shape: str,
    line_width: int = 2,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        values: List of numbers representing the values.
        dates: List of datetime objects for each of the values.
        shaded_section_fill_colour: The colour to use
            for the fill of the shaded/highlighted section.
        shaded_section_line_colour: The colour to use
            for the line of the shaded/highlighted section.
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
    line_plot: plotly.graph_objects.Scatter = _create_main_line_plot(
        dates=dates,
        values=values,
        preceding_data_points_count=preceding_data_points_count,
        line_width=line_width,
        line_shape=line_shape,
    )

    # Add line plot to the figure
    figure.add_trace(trace=line_plot)

    # Create the shaded section for the last `n` points
    # Where `n` is denoted by `rolling_period_slice`
    shaded_section_plot: plotly.graph_objects.Scatter = _create_shaded_section_plot(
        dates=dates,
        values=values,
        preceding_data_points_count=preceding_data_points_count,
        line_width=line_width,
        line_shape=line_shape,
        shaded_section_line_colour=shaded_section_line_colour.stringified,
        shaded_section_fill_colour=shaded_section_fill_colour.stringified,
    )

    # Add the highlighted section plot to the figure
    figure.add_trace(trace=shaded_section_plot)

    # Apply the typical stylings for timeseries charts
    figure.update_layout(**TIMESERIES_LAYOUT_ARGS)

    return figure


def _create_main_line_plot(
    dates: List[datetime.datetime],
    values: List[int],
    preceding_data_points_count: int,
    line_width: int,
    line_shape: str,
):
    return plotly.graph_objects.Scatter(
        x=dates[: preceding_data_points_count + 1],
        y=values[: preceding_data_points_count + 1],
        line={
            "width": line_width,
            "color": colour_scheme.RGBAColours.DARK_GREY.stringified,
        },
        line_shape=line_shape,
    )


def _create_shaded_section_plot(
    dates: List[datetime.datetime],
    values: List[int],
    preceding_data_points_count: int,
    line_width: int,
    line_shape: str,
    shaded_section_line_colour: str,
    shaded_section_fill_colour: str,
):
    return plotly.graph_objects.Scatter(
        x=dates[preceding_data_points_count:],
        y=values[preceding_data_points_count:],
        line={"width": line_width},
        mode="lines",
        fill="tozeroy",
        hoveron="points",
        opacity=0.5,
        line_color=shaded_section_line_colour,
        fillcolor=shaded_section_fill_colour,
        line_shape=line_shape,
    )


def generate_chart_figure(
    values: List[int],
    dates: List[datetime.datetime],
    metric_name: str,
    change_in_metric_value: int,
    rolling_period_slice: int = 7,
    line_shape: str = "spline",
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        values: List of numbers representing the values.
        dates: List of datetime objects for each of the values.
        metric_name: The associated metric_name,
            E.g. new_admissions_daily
        change_in_metric_value: The change in metric value from the last 7 days
            compared to the preceding 7 days.
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
        change_in_metric_value=change_in_metric_value,
        metric_name=metric_name,
    )

    return create_line_chart_with_shaded_section(
        values=values,
        dates=dates,
        rolling_period_slice=rolling_period_slice,
        line_shape=line_shape,
        shaded_section_line_colour=line_colour,
        shaded_section_fill_colour=fill_colour,
    )
