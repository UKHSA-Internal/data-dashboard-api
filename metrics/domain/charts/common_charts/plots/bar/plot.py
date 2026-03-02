import plotly.graph_objects

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotGenerationData
from metrics.domain.models.plots import ChartGenerationPayload


def create_bar_plot(
    *, plot_data: PlotGenerationData, chart_generation_payload: ChartGenerationPayload
) -> dict:
    """Create a `bar` plot to add to the chart (via the add_trace method).

    Args:
        plot_data: The `PlotGenerationData` to build
        the bar plot for.

        chart_generation_payload: the `ChartGenerationPayload` to build the bar
        plot for

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
        error_y=get_error_bars(plot_data, chart_generation_payload),
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


def get_error_bars(
    plot_data: PlotGenerationData, chart_generation_payload: ChartGenerationPayload
):
    """Add error bars to plot data if they've been requested and we have the
    data to do so

    Args:
        plot_data: The `PlotGenerationData` to build the bar plot for.

        chart_generation_payload: the `ChartGenerationPayload` to build the bar
        plot for

    Returns:
        Dictionary representation of the error object to be added
        to the plot.
    """

    if not chart_generation_payload.confidence_intervals:
        return None

    upper_confidence = plot_data.additional_values.get("upper_confidence", [])

    lower_confidence = plot_data.additional_values.get("lower_confidence", [])

    if len(upper_confidence) == 0 or len(lower_confidence) == 0:
        return None

    confidence_color: colour_scheme.RGBAChartLineColours = (
        colour_scheme.RGBAChartLineColours.get_colour(
            colour=chart_generation_payload.confidence_colour
        )
    )
    error_bar_colour: str = confidence_color.stringified

    # Plotly wants this as distances from the metric value rather than the
    # absolute values that we're given in data see https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.ErrorY.type

    # We may get some plots with confidence and some without so handle those
    # gracefully
    upper_values = [
        (confidence if confidence is not None else metric) - metric
        for confidence, metric in zip(
            upper_confidence, plot_data.y_axis_values, strict=True
        )
    ]

    lower_values = [
        metric - (confidence if confidence is not None else metric)
        for confidence, metric in zip(
            lower_confidence, plot_data.y_axis_values, strict=True
        )
    ]

    return {
        "type": "data",
        "array": upper_values,
        "arrayminus": lower_values,
        "color": error_bar_colour,
        "thickness": 1.5,
        "width": 3,
    }
