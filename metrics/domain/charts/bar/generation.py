import plotly.graph_objects

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotGenerationData


def create_bar_plot(
    *,
    plot_data: PlotGenerationData,
) -> dict:
    """Create a Bar plot to add to the chart (via the add_trace method)

    Args:
        x_axis_values: The values to display along the x-axis
        y_axis_values: The values to display along the y-axis
        bar_colour: The colour to assign to the bars.
        legend: Legend to display for this plot.

    Returns:
        Dictionary representation of the graph object
        which can be added to the figure

    """
    selected_colour: colour_scheme.RGBAChartLineColours = (
        colour_scheme.RGBAChartLineColours.get_colour(
            colour=plot_data.parameters.line_colour
        )
    )
    bar_colour: str = selected_colour.stringified
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
        name=legend,
        showlegend=bool(legend),
    )

    return convert_graph_object_to_dict(graph_object=bar)
