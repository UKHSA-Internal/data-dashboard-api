from typing import Any

import plotly

from metrics.domain.charts import chart_settings, colour_scheme
from metrics.domain.charts.line_with_shaded_section import information
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotData


def create_line_chart_with_shaded_section(
    *,
    plots_data: list[PlotData],
    chart_height: int,
    chart_width: int,
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    shaded_section_fill_colour: colour_scheme.RGBAColours,
    shaded_section_line_colour: colour_scheme.RGBAColours,
    rolling_period_slice: int,
    line_shape: str,
    line_width: int = 2,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        plots_data: The list of enriched `PlotData` models
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        x_axis_values: The values for the x-axis
        y_axis_values: The values for the y-axis
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
    preceding_data_points_count = len(y_axis_values) - (rolling_period_slice + 1)

    figure = plotly.graph_objects.Figure()

    # Create the line plot for the preceding points as a simple neutral grey line
    line_plot: dict = _create_main_line_plot(
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        preceding_data_points_count=preceding_data_points_count,
        line_width=line_width,
        line_shape=line_shape,
    )

    # Add line plot to the figure
    figure.add_trace(trace=line_plot)

    # Create the shaded section for the last `n` points
    # Where `n` is denoted by `rolling_period_slice`
    shaded_section_plot: dict = _create_shaded_section_plot(
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        preceding_data_points_count=preceding_data_points_count,
        line_width=line_width,
        line_shape=line_shape,
        shaded_section_line_colour=shaded_section_line_colour.stringified,
        shaded_section_fill_colour=shaded_section_fill_colour.stringified,
    )

    # Add the highlighted section plot to the figure
    figure.add_trace(trace=shaded_section_plot)

    # Apply the typical stylings for timeseries charts
    settings = chart_settings.ChartSettings(
        width=chart_width, height=chart_height, plots_data=plots_data
    )
    layout_args = settings.get_line_with_shaded_section_chart_config()
    figure.update_layout(**layout_args)

    return figure


def _create_main_line_plot(
    *,
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    preceding_data_points_count: int,
    line_width: int,
    line_shape: str,
) -> dict:
    graph_object = plotly.graph_objects.Scatter(
        x=x_axis_values[: preceding_data_points_count + 1],
        y=y_axis_values[: preceding_data_points_count + 1],
        line={
            "width": line_width,
            "color": colour_scheme.RGBAColours.LS_DARK_GREY.stringified,
        },
        line_shape=line_shape,
    )
    return convert_graph_object_to_dict(graph_object=graph_object)


def _create_shaded_section_plot(
    *,
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    preceding_data_points_count: int,
    line_width: int,
    line_shape: str,
    shaded_section_line_colour: str,
    shaded_section_fill_colour: str,
) -> dict:
    scatter = plotly.graph_objects.Scatter(
        x=x_axis_values[preceding_data_points_count:],
        y=y_axis_values[preceding_data_points_count:],
        line={"width": line_width},
        mode="lines",
        fill="tozeroy",
        hoveron="points",
        opacity=0.5,
        line_color=shaded_section_line_colour,
        fillcolor=shaded_section_fill_colour,
        line_shape=line_shape,
    )
    return convert_graph_object_to_dict(graph_object=scatter)


def generate_chart_figure(
    *,
    plots_data: list[PlotData],
    chart_height: int,
    chart_width: int,
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    metric_name: str,
    change_in_metric_value: int,
    rolling_period_slice: int = 7,
    line_shape: str = "spline",
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        plots_data: The list of enriched `PlotData` models
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        x_axis_values: The values for the x-axis
        y_axis_values: The values for the y-axis
        metric_name: The associated metric_name,
            E.g. `new_admissions_daily`
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
        plots_data=plots_data,
        chart_height=chart_height,
        chart_width=chart_width,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        rolling_period_slice=rolling_period_slice,
        line_shape=line_shape,
        shaded_section_line_colour=line_colour,
        shaded_section_fill_colour=fill_colour,
    )
