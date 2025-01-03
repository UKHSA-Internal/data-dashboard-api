import logging

import plotly
from plotly.graph_objs import Scatter

from metrics.domain.models import PlotGenerationData
from metrics.domain.models.plots import (
    NoReportingDelayPeriodFoundError,
    ReportingDelayNotProvidedToPlotsError,
)

CYAN = "#0090C6"
LIGHT_BLUE = "#D2E9F1"

logger = logging.getLogger(__name__)


def _get_last_x_value_at_end_of_reporting_delay_period(
    figure: plotly.graph_objs.Figure,
) -> str:
    latest_dates: list[str] = [max(plot["x"]) for plot in figure.data]
    return max(latest_dates)


def get_x_value_at_start_of_reporting_delay_period(
    chart_plots_data: list[PlotGenerationData],
) -> str:
    index: int = chart_plots_data[0].start_of_reporting_delay_period_index
    return chart_plots_data[0].x_axis_values[index]


def add_reporting_delay_period(
    chart_plots_data: list[PlotGenerationData],
    figure: plotly.graph_objects.Figure,
    boundary_colour: str = CYAN,
    fill_colour: str = LIGHT_BLUE,
) -> None:
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
    try:
        start_x_of_reporting_delay: str = (
            get_x_value_at_start_of_reporting_delay_period(
                chart_plots_data=chart_plots_data
            )
        )
    except (ReportingDelayNotProvidedToPlotsError, NoReportingDelayPeriodFoundError):
        return

    last_x_of_reporting_delay: str = _get_last_x_value_at_end_of_reporting_delay_period(
        figure=figure
    )

    fill_opacity = 0.6
    # Draw the shaded section of the reporting delay period
    figure.add_vrect(
        x0=start_x_of_reporting_delay,
        x1=last_x_of_reporting_delay,
        fillcolor=fill_colour,
        opacity=fill_opacity,
        line_width=0,
    )

    # Draw the boundaries of the reporting delay period
    figure.add_vline(
        x=start_x_of_reporting_delay, line_color=boundary_colour, line_width=2
    )
    figure.add_vline(
        x=last_x_of_reporting_delay, line_color=boundary_colour, line_width=2
    )

    # Add a dummy trace to include the reporting delay period
    # in the rendered legend
    figure.add_trace(
        trace=Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={
                "color": fill_colour,
                "opacity": fill_opacity,
                "symbol": "square",
                "size": 15,
                "line": {"color": boundary_colour, "width": 2},
            },
            name="Reporting delay",
        )
    )
