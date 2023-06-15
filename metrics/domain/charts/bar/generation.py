from datetime import date
from typing import Any, List

import plotly.graph_objects

from metrics.domain.charts import chart_settings, colour_scheme


def generate_chart_figure(
    chart_height: int,
    chart_width: int,
    x_axis_values: List[Any],
    y_axis_values: List[Any],
    legend: str,
    bar_colour: str = colour_scheme.RGBAColours.BAR_PLOT_1_BLUE.stringified,
) -> plotly.graph_objects.Figure:
    """Creates a `Figure` object for the given `dates` & `values` as a Bar graph.

    Args:
        chart_height: The chart height in pixels
        chart_width: The chart width in pixels
        x_axis_values: The values to display along the x-axis
        y_axis_values: The values to display along the y-axis
        legend: Legend associated with the given plot
        bar_colour: The colour to assign to the bar.
            Defaults to 86, 148, 202, 1, blue.

    Returns:
        `Figure`: A `plotly` object which can then be
            written to a file, or shown
    """

    figure = plotly.graph_objects.Figure()

    # Create Bar plot
    bar_plot: plotly.graph_objects.Bar = _create_bar_plot(
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        bar_colour=bar_colour,
        legend=legend,
        showlegend=bool(legend),
    )

    # Add plot to graph
    figure.add_trace(trace=bar_plot)

    settings = chart_settings.ChartSettings(
        width=chart_width, height=chart_height, plots_data=x_axis_values
    )

    layout_args = settings.get_base_chart_config()
    figure.update_layout(**layout_args)

    # Apply the typical stylings for bar charts
    figure.update_layout(
        **{
            "showlegend": True,
            "barmode": "group",
            "legend": {
                "orientation": "h",
                "y": -0.15,
                "x": 0,
            },
        }
    )

    # Set x axis tick type depending on what sort of data we are showing
    if type(x_axis_values[0]) is date:
        figure.update_xaxes(**settings._get_x_axis_date_type())

        # Give the chart the best chance of displaying all the tick labels
        min_date, max_date = chart_settings.get_x_axis_range(figure=figure)

        figure.update_xaxes(range=[min_date, max_date])
        figure.update_layout(**settings._get_margin_for_charts_with_dates())
    else:
        figure.update_xaxes(**settings._get_x_axis_text_type())

    # We want to see tick labels on the Y Axis
    figure.update_yaxes(showticklabels=True)

    return figure


def _create_bar_plot(
    x_axis_values: List[Any],
    y_axis_values: List[Any],
    bar_colour: str,
    legend: str,
    showlegend: bool = False,
) -> plotly.graph_objects.Bar:
    """Create a Bar plot to add to the chart (via the add_trace method)

    Args:
        x_axis_values: The values to display along the x-axis
        y_axis_values: The values to display along the y-axis
        bar_colour: The colour to assign to the bars.
        legend: Legend to display for this plot.
        showlegend: Whether or not to display the associated legend for this plot
            Note: showlegend in BAR_CHART_LAYOUT_ARGS constant has to be True
            for this setting to have any effect
    Returns:
        `Bar`: A `plotly` bar which can then be added to the chart
    """

    return plotly.graph_objects.Bar(
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
        showlegend=showlegend,
    )
