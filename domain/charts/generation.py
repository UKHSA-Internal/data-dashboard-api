from typing import List, Union

import plotly.graph_objects

NUMBER = Union[int, float]

BLACK = "#000000"
GREY = "#F3F2F1"
LIGHT_GREY = "#F8F8F8"


def generate_chart_figure(
    data_points: List[NUMBER],
    line_color: str = BLACK,
    area_fill_color: str = GREY,
    background_color: str = LIGHT_GREY,
    line_shape: str = "spline",
    line_width: int = 3,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `data_points`

    Args:
        data_points: list of floats or ints representing the points to be plotted
        line_color: The color to assign to the line.
            Defaults to #000000, black.
        area_fill_color: The color to assign to the shaded area under the line plot.
            Defaults to #F3F2F1, a darker shade of grey
        background_color: The color to assign to the background of the plot.
            Defaults to #F8F8F8, a lighter shade of grey
        line_shape: The shape to assign to the line plots.
            Defaults to "spline", a curved shape between points.
        line_width: The weight to assign to the width of the line plots.
            Defaults to 3.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown

    Notes:
        The size of the markers associated with each data point
        is calculated as `line_width` * 3.
        This is so that the markers are clearly visible against
        the weight of the line plots.

    """
    data_points_count: int = len(data_points)
    x_points: List[int] = [index for index in range(data_points_count)]

    figure = plotly.graph_objects.Figure()

    # Create the line plot object
    line_plot = plotly.graph_objects.Scatter(
        x=x_points,
        y=data_points,
        fill="tozeroy",
        fillcolor=area_fill_color,
        line_shape=line_shape,
        line={"color": line_color, "width": line_width},
        marker={"symbol": "circle", "size": line_width * 3},
    )

    # Add line plot to the figure
    figure.add_trace(
        trace=line_plot,
    )

    # Remove gridlines and apply custom background color
    remove_gridlines_args = {"visible": False}
    figure.update_layout(
        yaxis=remove_gridlines_args,
        xaxis=remove_gridlines_args,
        plot_bgcolor=background_color,
    )

    # Over a certain threshold, plotly will convert the scatter plot to a line plot
    # and therefore remove the markers.
    # This setting re-adds the markers to the plot
    figure.data[0].mode = "lines+markers"

    return figure
