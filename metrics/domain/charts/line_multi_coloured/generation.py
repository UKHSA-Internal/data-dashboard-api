import datetime
from typing import List

import plotly

from metrics.domain.charts import chart_settings, type_hints
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured import properties
from metrics.domain.models import PlotsData

LAYOUT_ARGS: type_hints.CHART_ARGS = chart_settings.CHART_SETTINGS | {
    "legend": {
        "orientation": "h",
        "y": 1.0,
        "x": 0.5,
        "xanchor": "center",
        "yanchor": "bottom",
    },
}


def create_multi_coloured_line_chart(
    chart_height: int,
    chart_width: int,
    chart_plots_data: List[PlotsData],
    line_shape: str,
    line_width: int = 2,
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        chart_plots_data: List of `ChartPlotData` models,
            where each model represents a requested plot.
        line_shape: The shape to assign to the line plots.
            This can be either `linear` or `spline`.
        line_width: The weight to assign to the width of the line plots.
            Defaults to 2.
    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    figure = plotly.graph_objects.Figure()

    for plot_data in chart_plots_data:
        selected_colour = RGBAChartLineColours.get_colour(
            colour=plot_data.parameters.line_colour
        )
        selected_line_type = properties.ChartLineTypes.get_chart_line_type(
            line_type=plot_data.parameters.line_type
        )

        line_plot: plotly.graph_objects.Scatter = _create_line_plot(
            x_axis=plot_data.x_axis_values,
            y_axis=plot_data.y_axis_values,
            colour=selected_colour.stringified,
            line_width=line_width,
            line_shape=line_shape,
            legend=plot_data.parameters.label,
            dash=selected_line_type.value,
        )

        # Add line plot to the figure
        figure.add_trace(trace=line_plot)

    # Apply the typical stylings for timeseries charts
    figure.update_layout(**LAYOUT_ARGS)

    # Set the height and width of the chart itself
    figure.update_layout(
        {
            "height": chart_height,
            "width": chart_width,
            "showlegend": properties.is_legend_required(
                chart_plots_data=chart_plots_data
            ),
        }
    )

    return figure


def _create_line_plot(
    x_axis: List[datetime.datetime],
    y_axis: List[int],
    colour: str,
    line_width: int,
    line_shape: str,
    legend: str,
    dash: str,
):
    return plotly.graph_objects.Scatter(
        x=x_axis,
        y=y_axis,
        line={
            "width": line_width,
            "color": colour,
            "dash": dash,
        },
        line_shape=line_shape,
        name=legend,
    )


def generate_chart_figure(
    chart_height: int,
    chart_width: int,
    chart_plots_data: List[PlotsData],
    line_shape: str = "spline",
) -> plotly.graph_objs.Figure:
    """Creates a `Figure` object for the given `chart_plots_data` as a graph with multiple line plots.

    Args:
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        chart_plots_data: List of `ChartPlotData` models,
            where each model represents a requested plot.
        line_shape: The shape to assign to the line plots.
            This can be either `linear` or `spline`.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown.

    """
    return create_multi_coloured_line_chart(
        chart_height=chart_height,
        chart_width=chart_width,
        chart_plots_data=chart_plots_data,
        line_shape=line_shape,
    )
