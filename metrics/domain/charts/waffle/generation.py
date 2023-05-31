from typing import Dict, List, Union

import plotly.graph_objects
from numpy.core.multiarray import ndarray

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.waffle import pre_processing, validation
from metrics.domain.charts.waffle.colour_scheme import build_color_scale

X_AXIS_ARGS: Dict[str, bool] = {
    "showgrid": False,
    "ticks": None,
    "showticklabels": False,
}

Y_AXIS_ARGS: Dict[str, Union[bool, int, str]] = {
    **X_AXIS_ARGS,
    **{"scaleratio": 1, "scaleanchor": "x"},
}


WAFFLE_LAYOUT_ARGS = {
    "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
    "showlegend": False,
    "plot_bgcolor": colour_scheme.RGBAColours.LIGHT_GREY.stringified,
    "paper_bgcolor": colour_scheme.RGBAColours.WAFFLE_WHITE.stringified,
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
}


def generate_chart_figure(
    values: List[int],
    cell_gap: int = 3,
    width: int = 400,
    height: int = 400,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `values` as a Waffle chart.

    Args:
        values: List of integers representing the points to be plotted
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
        `DataPointsNotInDescendingOrderError: If the given
            `values` are not in descending order.
            From largest to smallest values, left to right.

    """
    validation._check_values(values=values)

    figure = plotly.graph_objects.Figure()

    for index, value in enumerate(values, 1):
        figure = _add_plot_to_figure(
            value=int(value), index=index, cell_gap=cell_gap, figure=figure
        )

    figure.update_layout(width=width, height=height, **WAFFLE_LAYOUT_ARGS)

    return figure


def _add_plot_to_figure(
    value: int, index: int, cell_gap: int, figure: plotly.graph_objects.Figure
) -> plotly.graph_objects.Figure:
    # Build 2D matrix to represent the given `value`
    two_dimensional_matrix: ndarray = pre_processing.build_two_dimensional_matrix(
        threshold=value, identifier=index
    )

    # Fetch the colour scale values based on the index
    colour_scale: List[List] = build_color_scale(identifier=index)

    # Create the heatmap plot
    heatmap_plot = plotly.graph_objects.Heatmap(
        z=two_dimensional_matrix,
        hoverongaps=False,
        showscale=False,
        ygap=cell_gap,
        xgap=cell_gap,
        colorscale=colour_scale,
    )

    # Add the heatmap plot to the chart
    figure.add_trace(trace=heatmap_plot)

    return figure
