import plotly.graph_objects
from plotly.subplots import make_subplots

from metrics.domain.models.subplot_plots import (
    SubplotChartGenerationPayload,
    SubplotGenerationData,
)


def generate_chart_figure(
    *,
    chart_generation_payload: SubplotChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    subplot_data: list[SubplotGenerationData] = chart_generation_payload.subplot_data

    figure = make_subplots(
        rows=1,
        cols=len(subplot_data),
        shared_xaxes=True,
        horizontal_spacing=0,
        subplot_titles=[subplot.subplot_title for subplot in subplot_data],
    )

    for plot_index, plot_data in enumerate(subplot_data, start=1):
        for data in plot_data.subplot_data:
            figure.add_trace(
                plotly.graph_objects.Bar(
                    x=data.x_axis_values,
                    y=data.y_axis_values,
                    name=getattr(data.parameters, "geography", None),
                ),
                row=1,
                col=plot_index,
            )
            if plot_index > 1:
                figure.update_yaxes(showticklabels=False, row=1, col=plot_index)

    if chart_generation_payload.target_threshold:
        add_threshold_bar(figure, y_bottom=chart_generation_payload.target_threshold)

    return figure


def add_threshold_bar(
    figure: plotly.graph_objs.Figure,
    y_bottom: float,
    fill_colour: str = "rgba(135, 206, 235, 0.3)",
    label: str = "95% target",
):
    """Add a blue bar with solid top line and dashed bottom line to a Plotly figure.

    Notes:
        The bar automatically spans the full width of the chart
        and extends to the top.

    Args:
        figure: The Plotly figure object to add the threshold bar to
        y_bottom: Y-coordinate for the bottom of the bar
            i.e. the threshold value
        fill_colour: Colour for the filled bar area (with transparency)
        label : Label for the threshold indicator (appears in legend)

    Returns:
        The modified plotly figure object
        with the threshold bar added

    """
    line_color = "blue"
    computed_figure = figure.full_figure_for_development()
    y_top: float = computed_figure.layout.yaxis.range[1]

    y_top = _round_to_significant_figure(number=y_top, significant_digits=3)

    figure.add_hline(
        y=y_top,
        line={"color": line_color, "width": 2, "dash": "solid"},
        layer="below",
    )
    figure.add_hrect(
        type="rect",
        y0=y_bottom,
        y1=y_top,
        fillcolor=fill_colour,
        line={"width": 0},
        layer="below",
    )
    figure.add_hline(
        y=y_bottom,
        line={"color": line_color, "width": 2, "dash": "dash"},
        layer="below",
    )

    # Add invisible trace for legend entry
    figure.add_trace(
        plotly.graph_objs.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line={"color": fill_colour, "width": 8},
            name=label,
            showlegend=True,
        )
    )

    return figure


def _round_to_significant_figure(*, number: float, significant_digits: int) -> float:
    return float(format(number, f".{significant_digits}g"))
