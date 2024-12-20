from datetime import datetime
from decimal import Decimal

import plotly.graph_objects

from metrics.domain.charts import chart_settings
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.models.plots import ChartGenerationPayload


def create_simplified_line_chart(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload` model
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.


    Returns:
        `Figure`: A `Plotly` object which can be
            written to a file, or shown.
    """
    figure = plotly.graph_objects.Figure()
    chart_plot = chart_generation_payload.plots[0]

    selected_colour = RGBAChartLineColours.get_colour(
        colour=chart_plot.parameters.line_colour
    )

    line_shape = "spline" if chart_plot.parameters.use_smooth_lines else "linear"

    line_plot: dict = _create_line_plot(
        x_axis_values=chart_plot.x_axis_values,
        y_axis_values=chart_plot.y_axis_values,
        line_shape=line_shape,
        colour=selected_colour.stringified,
    )

    figure.add_trace(trace=line_plot)

    settings = chart_settings.ChartSettings(
        chart_generation_payload=chart_generation_payload
    )

    layout_args = settings.get_line_single_simplified_chart_config()
    figure.update_layout(**layout_args)

    return figure


def _create_line_plot(
    *,
    x_axis_values: list[datetime.date],
    y_axis_values: list[Decimal],
    colour: str,
    line_shape: str,
) -> dict:
    return plotly.graph_objects.Scatter(
        x=x_axis_values,
        y=y_axis_values,
        mode="lines",
        line={"color": colour, "width": 3},
        line_shape=line_shape,
    )


def generate_chart_figure(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a
        simplified line graph with a single plot and 4 axis ticks

    Args:
        chart_generation_payload: An enriched `ChartGenerationPayload`
            which holds all the parameters like colour and plot labels
             along with the corresponding x and y values
             which are needed to be able to generate the chart in full.


    Returns:
        `Figure`: A `Plotly` object which can then be
            written to a file, or shown.

    """
    return create_simplified_line_chart(
        chart_generation_payload=chart_generation_payload
    )
