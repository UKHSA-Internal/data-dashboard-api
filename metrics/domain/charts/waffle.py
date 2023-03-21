from typing import Dict, List, Union

import numpy as np
import plotly.graph_objects


def build_two_dimensional_matrix(
    threshold: int, identifier: int, length: int = 10, width: int = 10
) -> np.ndarray:
    """Builds a 2D matrix with the `identifier` as the non-zero value.

    Notes:
        If the `identifier` is not given as `1`,
        then all non-zero values will become `NaN` values.
        The `length` and `width` default to 10.
        This means that by default the returned matrix will be
        of size `100`.

    Args:
        threshold: The nominal point of non-zero values in the matrix
        identifier: The number to assign to the non-zero values.
        length: The size in the y-axis to build the matrix to.
            Defaults to 10
        width: The size in the x-axis to build the matrix to.
            Defaults to 10

    Returns:
        np.ndarray: A 2D array of the shape dicated
        by the given `length` and `width` values.
        E.g. With the following:
            identifier = 1
            length = 2
            width = 2
            threshold = 2
        >>> array([[1., 0.], [0., 0.]])

    """
    matrix_size: int = length * width
    data: np.ndarray = np.zeros(shape=matrix_size)

    if identifier > 1:
        data[:] = np.NaN

    data[:threshold] = identifier
    return data.reshape([width, length])


X_AXIS_ARGS: Dict[str, bool] = {
    "showgrid": False,
    "ticks": None,
    "showticklabels": False,
}

Y_AXIS_ARGS: Dict[str, Union[bool, int, str]] = {
    **X_AXIS_ARGS,
    **{"scaleratio": 1, "scaleanchor": "x"},
}


WAFFLE_LAYOUT = {
    "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
    "showlegend": False,
    "plot_bgcolor": "rgba(231,231,231,0)",
    "paper_bgcolor": "rgba(255,255,255,0)",
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
}


RGB_COLOURS = {
    "light_grey": "216,216,216,1",
    "light_green": "119,196,191,1",
    "middle_green": "0,156,145,1",
    "dark_green": "0,65,61,1",
}


def get_rgb_colour(colour: str) -> str:
    """Gets the RGBA colour representation as required by `plotly`

    Args:
        colour: A human-readable colour.
            >>> 'dark_green'

    Returns:
        str: The RGBA representation.
            >>> 'rgba(0,65,61,1)'

    Raises:
        `KeyError`: If the colour is not supported

    """
    rgb_number = RGB_COLOURS[colour]
    return f"rgba({rgb_number})"


class InvalidIdentifierError(Exception):
    ...


def build_color_scale(identifier: int) -> List[List]:
    """Builds the colour scale for the waffle chart plot based on the identifier.

    Args:
        identifier: The position of the plot.
            Currently, this can only be 1, 2 or 3.

    Returns:
        List[list[int, str]]: A nested list of values.
            >>> [
                    [0, 'rgba(216,216,216,1)'],
                    [0.5, 'rgba(0,156,145,1)'],
                    [0.9, 'rgba(0,156,145,1)'],
                    [1, 'rgba(0,156,145,1)'],
            ]

    Raises:
        `InvalidIdentifierError`: If an identifier which is not
            either 1, 2 or 3 is provided.

    """
    background_rgb_colour: str = get_rgb_colour(colour="light_grey")

    if identifier == 3:
        darkest_plot_rgb_colour: str = get_rgb_colour(colour="dark_green")
        return [
            [0, background_rgb_colour],
            [0.5, darkest_plot_rgb_colour],
            [0.9, darkest_plot_rgb_colour],
            [1, darkest_plot_rgb_colour],
        ]

    if identifier == 2:
        middle_plot_rgb_colour: str = get_rgb_colour(colour="middle_green")
        return [
            [0, background_rgb_colour],
            [0.5, middle_plot_rgb_colour],
            [0.9, middle_plot_rgb_colour],
            [1, middle_plot_rgb_colour],
        ]
    if identifier == 1:
        lightest_plot_rgb_colour: str = get_rgb_colour(colour="light_green")
        return [
            [0, background_rgb_colour],
            [0.5, background_rgb_colour],
            [0.9, lightest_plot_rgb_colour],
            [1, lightest_plot_rgb_colour],
        ]

    raise InvalidIdentifierError()


class TooManyDataPointsError(Exception):
    ...


def generate_chart_figure(
    data_points: List[int],
    cell_gap: int = 3,
    width: int = 400,
    height: int = 400,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `data_points` as a Waffle chart.

    Args:
        data_points: List of integers representing the points to be plotted
        cell_gap: The width to allow between each displayed cell.
            Defaults to 3.
        width: The width in pixels to assign to the figure.
            Defaults to 400.
        height: TThe length in pixels to assign to the figure.
            Defaults to 400.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown

    Raises:
        `TooManyDataPointsWaffleChartError`: If more than
            3 data points are provided

    """
    if len(data_points) > 3:
        raise TooManyDataPointsError()

    figure = plotly.graph_objects.Figure()

    for index, value in enumerate(data_points, 1):
        logical_matrix: np.ndarray = build_two_dimensional_matrix(
            threshold=value, identifier=index
        )

        # Fetch the colour scale values based on the index
        colour_scale: List[List] = build_color_scale(identifier=index)

        # Create the heatmap plot
        heatmap_plot = plotly.graph_objects.Heatmap(
            z=logical_matrix,
            hoverongaps=False,
            showscale=False,
            ygap=cell_gap,
            xgap=cell_gap,
            colorscale=colour_scale,
        )

        # Add the heatmap plot to the chart
        figure.add_trace(trace=heatmap_plot)

    figure.update_layout(width=width, height=height, **WAFFLE_LAYOUT)

    return figure
