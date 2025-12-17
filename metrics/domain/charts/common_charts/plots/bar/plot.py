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

    if "upper_confidence" in plot_data.additional_values:
        upper_error = [x-y for x, y in zip(
            plot_data.additional_values["upper_confidence"],
            plot_data.y_axis_values
        )]
        lower_error = [x-y for x, y in zip(
            plot_data.y_axis_values,
            plot_data.additional_values["lower_confidence"]
        )]
        confidence_color: colour_scheme.RGBAChartLineColours = (
            colour_scheme.RGBAChartLineColours.get_colour(
                colour=plot_data.parameters.confidence_colour
            )
        )
        error_bar_colour: str = confidence_color.stringified
        error_y = dict(
            type='data',
            array=upper_error,
            arrayminus=lower_error,
            color=error_bar_colour,
            thickness=1.5,
            width=3,
        )
    else:
        error_y = None

    bar = plotly.graph_objects.Bar(
        x=plot_data.x_axis_values,
        y=plot_data.y_axis_values,
        error_y=error_y,
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
