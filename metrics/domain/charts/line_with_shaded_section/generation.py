import datetime
from typing import List

import plotly

from metrics.domain.charts.line_with_shaded_section.colour_scheme import RGBAColours

X_AXIS_ARGS = {
    "showgrid": False,
    "zeroline": False,
    "showline": False,
    "ticks": "outside",
    "tickson": "boundaries",
    "type": "date",
    "tickformat": "%b",
    "tickfont": {
        "family": '"GDS Transport", Arial, sans-serif',
        "size": 20,
        "color": RGBAColours.DARK_BLUE_GREY.stringified,
    },
}

Y_AXIS_ARGS = {
    "showgrid": False,
    "showticklabels": False,
}

TIMESERIES_LAYOUT_ARGS = {
    "paper_bgcolor": RGBAColours.WHITE.stringified,
    "plot_bgcolor": RGBAColours.WHITE.stringified,
    "margin": {
        "l": 0,
        "r": 0,
        "b": 4,
        "t": 0,
    },
    "showlegend": False,
    "height": 350,
    "autosize": False,
    "xaxis": X_AXIS_ARGS,
    "yaxis": Y_AXIS_ARGS,
}


def create_line_chart(
    dates: List[datetime.datetime],
    values: List[int],
    highlighted_section_fill_colour: RGBAColours,
    highlighted_section_line_colour: RGBAColours,
    rolling_period_slice: int,
    line_shape: str,
) -> str:
    preceding_data_points_count = len(values) - (rolling_period_slice + 1)

    # Add the line plot which is drawn with a simple neutral grey line
    figure = plotly.graph_objects.Figure(
        plotly.graph_objects.Scatter(
            x=dates[: preceding_data_points_count + 1],
            y=values[: preceding_data_points_count + 1],
            line={"width": 2, "color": RGBAColours.DARK_GREY.stringified},
            line_shape="spline",
        ),
    )

    # Add the rolling section to highlight whether its green or red
    figure.add_trace(
        plotly.graph_objects.Scatter(
            x=dates[preceding_data_points_count:],
            y=values[preceding_data_points_count:],
            line={"width": 2},
            mode="lines",
            fill="tozeroy",
            hoveron="points",
            opacity=0.5,
            line_color=highlighted_section_line_colour.stringified,
            fillcolor=highlighted_section_fill_colour.stringified,
            line_shape=line_shape,
        )
    )

    figure.update_layout(**TIMESERIES_LAYOUT_ARGS)

    return figure


def generate_chart_figure(
    dates: List[datetime.datetime],
    values: List[int],
    rolling_period_slice: int = 7,
    line_shape: str = "spline",
) -> str:
    return create_line_chart(
        dates=dates,
        values=values,
        rolling_period_slice=rolling_period_slice,
        line_shape=line_shape,
        highlighted_section_fill_colour=RGBAColours.LIGHT_GREEN.stringified,
        highlighted_section_line_colour=RGBAColours.DARK_GREEN.stringified,
    )
