from typing import List, Union

import plotly.graph_objects

from metrics.domain.charts.line import colour_scheme

AXIS_ARGS = {"visible": False}

LAYOUT_ARGS = {
    "xaxis": AXIS_ARGS,
    "yaxis": AXIS_ARGS,
}


def generate_chart_figure(
    data_points: List[Union[int, float]],
    line_color: str = colour_scheme.RGBAColours.BLACK.stringified,
    area_fill_color: str = colour_scheme.RGBAColours.DARK_GREY.stringified,
    background_color: str = colour_scheme.RGBAColours.LIGHT_GREY.stringified,
    line_shape: str = "spline",
    line_width: int = 3,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `data_points` as a Line graph.

    Notes:
        The size of the markers associated with each data point
        is calculated as `line_width` * 3.
        This is so that the markers are clearly visible against
        the weight of the line plots.

    Args:
        data_points: list of floats or ints representing the points to be plotted
        line_color: The color to assign to the line.
            Defaults to 0, 0, 0, 1, black.
        area_fill_color: The color to assign to the shaded area under the line plot.
            Defaults to 243, 242, 241, 1, a darker shade of grey
        background_color: The color to assign to the background of the plot.
            Defaults to 248, 248, 248, 1, a lighter shade of grey
        line_shape: The shape to assign to the line plots.
            Defaults to "spline", a curved shape between points.
        line_width: The weight to assign to the width of the line plots.
            Defaults to 3.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown

    """
    data_points_count: int = len(data_points)
    x_points: List[int] = [index for index in range(data_points_count)]

    figure = plotly.graph_objects.Figure()

    # Create the line plot object
    line_plot = _create_line_plot(
        data_points=data_points,
        x_points=x_points,
        area_fill_colour=area_fill_color,
        line_colour=line_color,
        line_shape=line_shape,
        line_width=line_width,
    )

    # Add line plot to the figure
    figure.add_trace(
        trace=line_plot,
    )

    layout_args = LAYOUT_ARGS
    layout_args["plot_bgcolor"] = background_color
    figure.update_layout(**layout_args)

    # Over a certain threshold, plotly will convert the scatter plot to a line plot
    # and therefore remove the markers.
    # This setting re-adds the markers to the plot
    figure.data[0].mode = "lines+markers"

    return figure


def _create_line_plot(
    data_points: List[int],
    x_points: List[int],
    area_fill_colour: str,
    line_colour: str,
    line_shape: str,
    line_width: int,
) -> plotly.graph_objects.Scatter:
    return plotly.graph_objects.Scatter(
        x=x_points,
        y=data_points,
        fill="tozeroy",
        fillcolor=area_fill_colour,
        line_shape=line_shape,
        line={"color": line_colour, "width": line_width},
        marker={"symbol": "circle", "size": line_width * 3},
    )
