from typing import Any

import plotly.graph_objects

from metrics.domain.charts import chart_settings, colour_scheme
from metrics.domain.charts.reporting_delay_period import add_reporting_delay_period
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import PlotGenerationData
from metrics.domain.models.plots import ChartGenerationPayload


def generate_chart_figure(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given chart payload as a Bar graph.

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload` model
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown

    """
    figure = plotly.graph_objects.Figure()

    chart_plots_data: list[PlotGenerationData] = chart_generation_payload.plots

    for plot_data in chart_plots_data:
        selected_colour: colour_scheme.RGBAChartLineColours = (
            colour_scheme.RGBAChartLineColours.get_colour(
                colour=plot_data.parameters.line_colour
            )
        )

        plot_label: str = plot_data.parameters.label

        # Create Bar plot
        bar_plot: dict = _create_bar_plot(
            x_axis_values=plot_data.x_axis_values,
            y_axis_values=plot_data.y_axis_values,
            bar_colour=selected_colour.stringified,
            legend=plot_label,
        )

        # Add plot to graph
        figure.add_trace(trace=bar_plot)

    settings = chart_settings.ChartSettings(
        chart_generation_payload=chart_generation_payload
    )

    layout_args = settings.get_bar_chart_config()
    figure.update_layout(**layout_args)

    if settings.is_date_type_x_axis:
        add_reporting_delay_period(
            chart_plots_data=chart_plots_data,
            figure=figure,
        )

    return figure


def _create_bar_plot(
    *,
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    bar_colour: str,
    legend: str,
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
    bar = plotly.graph_objects.Bar(
        x=x_axis_values,
        y=y_axis_values,
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
