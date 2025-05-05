import plotly

from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.common_charts.plots.line_multi_coloured.properties import (
    ChartLineTypes,
)
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotGenerationData


def create_line_plot(*, plot_data: PlotGenerationData) -> dict:
    """Creates a `line` plot to add to the chart (via the add_trace method).

    Args:
        plot_data: The `PlotGenerationData` object to build
        the line plot for.

    Returns:
        Dictionary representation of the graph object
        which can be added to the figure.
    """
    selected_colour = RGBAChartLineColours.get_colour(
        colour=plot_data.parameters.line_colour
    )
    selected_line_type = ChartLineTypes.get_chart_line_type(
        line_type=plot_data.parameters.line_type,
    )
    line_shape = "spline" if plot_data.parameters.use_smooth_lines else "linear"
    mode = "lines+markers" if plot_data.parameters.use_markers else "lines"
    legend = plot_data.parameters.label

    scatter = plotly.graph_objects.Scatter(
        x=plot_data.x_axis_values,
        y=plot_data.y_axis_values,
        mode=mode,
        line={
            "width": 2,
            "color": selected_colour.stringified,
            "dash": selected_line_type.value,
        },
        line_shape=line_shape,
        name=legend,
        showlegend=bool(legend),
    )

    return convert_graph_object_to_dict(graph_object=scatter)
