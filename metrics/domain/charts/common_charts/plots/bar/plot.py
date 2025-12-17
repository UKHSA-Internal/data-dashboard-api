import plotly.graph_objects

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotGenerationData


def create_bar_plot(
    *,
    plot_data: PlotGenerationData,
) -> dict:
    """Create a `bar` plot to add to the chart (via the add_trace method).

    Args:
        plot_data: The `PlotGenerationData` to build
        the bar plot for.

    Returns:
        Dictionary representation of the graph object
        which can be added to the figure.
    """
    selected_color: colour_scheme.RGBAChartLineColours = (
        colour_scheme.RGBAChartLineColours.get_colour(
            colour=plot_data.parameters.line_colour
        )
    )
    bar_colour: str = selected_color.stringified
    legend: str = plot_data.parameters.label

    bar = plotly.graph_objects.Bar(
        x=plot_data.x_axis_values,
        y=plot_data.y_axis_values,
        marker={
            "color": bar_colour,
            "line": {
                "color": bar_colour,
                "width": 1,
            },
        },
        error_y={"type": "data", "array": plot_data.lower_confidence_values},
        name=legend,
        showlegend=bool(legend),
    )

    return convert_graph_object_to_dict(graph_object=bar)
