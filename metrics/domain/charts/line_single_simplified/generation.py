from datetime import datetime
from decimal import Decimal

import plotly.graph_objects

from metrics.domain.charts import chart_settings
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.models import PlotData


def create_simplified_line_chart(
    *,
    plot_data: PlotData,
    chart_height: int,
    chart_width: int,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `values` as a line graph with a shaded region.

    Args:
        plot_data: `PlotData` model
        chart_height: chart width as an integer
        chart_width: chart height as an integer

    Returns:
        `Figure`: A `Plotly` object which can be
            written to a file, or shown.
    """
    figure = plotly.graph_objects.Figure()

    selected_colour = RGBAChartLineColours.get_colour(
        colour=plot_data[0].parameters.line_colour
    )

    line_shape = "spline" if plot_data[0].parameters.use_smooth_lines else "linear"

    line_plot: dict = _create_line_plot(
        x_axis_values=plot_data[0].x_axis_values,
        y_axis_values=plot_data[0].y_axis_values,
        line_shape=line_shape,
        colour=selected_colour.stringified,
    )

    figure.add_trace(trace=line_plot)

    settings = chart_settings.ChartSettings(
        width=chart_width, height=chart_height, plots_data=plot_data
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
    plot_data: PlotData,
    chart_height: int,
    chart_width: int,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a
        simplified line graph with a single plot and 4 axis ticks

    Args:
        plot_data: A `PlotData` model
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels

    Returns:
        `Figure`: A `Plotly` object which can then be
            written to a file, or shown.
    """
    return create_simplified_line_chart(
        plot_data=plot_data,
        chart_height=chart_height,
        chart_width=chart_width,
    )
