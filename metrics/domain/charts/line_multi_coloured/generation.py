from typing import Any

import plotly

from metrics.domain.charts import chart_settings
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured import properties
from metrics.domain.charts.reporting_delay_period import add_reporting_delay_period
from metrics.domain.charts.serialization import convert_graph_object_to_dict
from metrics.domain.models import ChartGenerationPayload, PlotGenerationData


def create_multi_coloured_line_chart(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload` model
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    figure = plotly.graph_objects.Figure()
    chart_plots_data: list[PlotGenerationData] = chart_generation_payload.plots

    for plot_data in chart_plots_data:
        selected_colour = RGBAChartLineColours.get_colour(
            colour=plot_data.parameters.line_colour
        )
        selected_line_type = properties.ChartLineTypes.get_chart_line_type(
            line_type=plot_data.parameters.line_type
        )

        line_shape = "spline" if plot_data.parameters.use_smooth_lines else "linear"
        mode = "lines+markers" if plot_data.parameters.use_markers else "lines"

        line_plot: dict = _create_line_plot(
            x_axis_values=plot_data.x_axis_values,
            y_axis_values=plot_data.y_axis_values,
            colour=selected_colour.stringified,
            line_width=2,
            line_shape=line_shape,
            mode=mode,
            legend=plot_data.parameters.label,
            dash=selected_line_type.value,
        )

        # Add line plot to the figure
        figure.add_trace(trace=line_plot)

    # Apply the typical styling for timeseries charts
    settings = chart_settings.ChartSettings(
        chart_generation_payload=chart_generation_payload
    )
    layout_args = settings.get_line_multi_coloured_chart_config()
    figure.update_layout(**layout_args)

    if settings.is_date_type_x_axis:
        add_reporting_delay_period(
            chart_plots_data=chart_plots_data,
            figure=figure,
        )

    return figure


def _create_line_plot(
    *,
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    colour: str,
    line_width: int,
    line_shape: str,
    legend: str,
    dash: str,
    mode: str,
) -> dict:
    scatter = plotly.graph_objects.Scatter(
        x=x_axis_values,
        y=y_axis_values,
        mode=mode,
        line={
            "width": line_width,
            "color": colour,
            "dash": dash,
        },
        line_shape=line_shape,
        name=legend,
        showlegend=bool(legend),
    )
    return convert_graph_object_to_dict(graph_object=scatter)


def generate_chart_figure(
    *, chart_generation_payload: ChartGenerationPayload
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload`
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    return create_multi_coloured_line_chart(
        chart_generation_payload=chart_generation_payload
    )
