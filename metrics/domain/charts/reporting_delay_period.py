import plotly

from metrics.domain.models import PlotData

CYAN = "#0090C6"
LIGHT_BLUE = "#D2E9F1"


def _get_last_x_value_at_end_of_reporting_delay_period(
    figure: plotly.graph_objs.Figure,
) -> str:
    latest_dates: list[str] = [max(plot["x"]) for plot in figure.data]
    return max(latest_dates)


def _get_x_value_at_start_of_reporting_delay_period(
    chart_plots_data: list[PlotData],
) -> str:
    # The -4 is a placeholder and should be replaced
    # with the value passed down from the data itself.
    return chart_plots_data[0].x_axis_values[-4]


def add_reporting_delay_period(
    chart_plots_data: list[PlotData],
    figure: plotly.graph_objects.Figure,
    boundary_colour: str = CYAN,
    fill_colour: str = LIGHT_BLUE,
):
    """Adds a filled region representing the reporting delay period on the figure

    Args:
        `chart_plots_data` The list enriched `PlotData` models
            containing the plot parameters and associated data
        `figure`: The `plotly` object which can added and drawn to.
        `boundary_colour`: The hex colour to draw the boundary lines
            of the filled region with.
            Defaults to #0090C6, which is a cyan colour.
       `fill_colour`: The hex colour to draw the filled region with.
            Defaults to #D2E9F1, which is a light blue colour.

    """
    start_x_of_reporting_delay: str = _get_x_value_at_start_of_reporting_delay_period(
        chart_plots_data=chart_plots_data
    )
    last_x_of_reporting_delay: str = _get_last_x_value_at_end_of_reporting_delay_period(
        figure=figure
    )

    # Draw the shaded section of the reporting delay period
    figure.add_vrect(
        x0=start_x_of_reporting_delay,
        x1=last_x_of_reporting_delay,
        fillcolor=fill_colour,
        opacity=0.6,
        line_width=0,
    )

    # Draw the boundaries of the reporting delay period
    figure.add_vline(
        x=start_x_of_reporting_delay, line_color=boundary_colour, line_width=2
    )
    figure.add_vline(
        x=last_x_of_reporting_delay, line_color=boundary_colour, line_width=2
    )
