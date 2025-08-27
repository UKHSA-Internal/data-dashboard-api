import math

import plotly.graph_objects
from plotly.subplots import make_subplots

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.subplot_chart_settings import (
    SubplotChartSettings,
)
from metrics.domain.models.subplot_plots import (
    SubplotChartGenerationPayload,
    SubplotGenerationData,
)


def format_tick_text(*, tick_text: str) -> str:
    """Formats tick text to wrap onto two lines.

    Args:
        tick_text: The tick text for a subplot's centre tick mark.

    Returns:
        str: The formatted tick text that includes `<b>` and `<br>`
        tags based on the number of words in the title.

    """
    first_line, seperator, last_line = tick_text.partition("(")

    if seperator:
        return f"<b>{first_line.strip()}</b><br>{seperator}{last_line.strip()}"

    return f"<b>{first_line.strip()}</b>"


def format_legend_names(
    figure: plotly.graph_objects.Figure,
) -> tuple[plotly.graph_objects.Figure, set[str]]:
    """Updates the Plotly figure legend group to remove duplicate names

    Args:
        figure: Plotly figure object.

    Returns:
        Plotly figure object where the legend group
        has been updated to combine duplicate names
        into a single legend entry.
        Alongside a set of plot labels

    """
    plot_labels: set[str] = set()

    for plot in figure.data:
        name = plot.name
        plot.legendgroup = name
        plot.showlegend = name not in plot_labels
        plot_labels.add(name)

    return [figure, plot_labels]


def generate_chart_figure(
    *,
    chart_generation_payload: SubplotChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    settings = SubplotChartSettings(
        chart_generation_payload=chart_generation_payload,
    )
    subplot_data: list[SubplotGenerationData] = chart_generation_payload.subplot_data

    figure = make_subplots(
        cols=len(subplot_data), **settings.get_make_subplots_config()
    )

    for plot_index, plot_data in enumerate(subplot_data, start=1):
        for data in plot_data.subplot_data:
            figure.add_trace(
                plotly.graph_objects.Bar(
                    x=data.x_axis_values,
                    y=data.y_axis_values,
                    name=getattr(
                        data.parameters,
                        data.parameters.x_axis,
                        None,
                    ),
                    marker={
                        "color": (
                            colour_scheme.RGBAChartLineColours.get_colour(
                                colour=data.parameters.line_colour,
                            ).stringified,
                        )
                    },
                ),
                row=1,
                col=plot_index,
            )

        figure.update_xaxes(
            col=plot_index,
            ticktext=[format_tick_text(tick_text=plot_data.subplot_title)],
            tickvals=[math.ceil(len(plot_data.subplot_data) / 2) - 1],
        )

    [figure, plot_labels] = format_legend_names(figure)

    figure.update_layout(
        **settings.get_subplot_chart_config(number_of_legend_items=len(plot_labels))
    )
    figure.update_yaxes(**settings.get_subplot_yaxis_config())
    figure.update_xaxes(**settings.get_subplot_xaxis_config())

    # Update primary y-axis settings (first subplot)
    figure.update_yaxes(**settings.get_primary_subplot_yaxis_config())

    figure.update_layout(**settings.get_x_axis_title_as_annotation_config())

    if chart_generation_payload.target_threshold:
        figure = add_target_threshold(
            figure=figure,
            y_bottom=chart_generation_payload.target_threshold,
            target_threshold_label=chart_generation_payload.target_threshold_label,
        )

    return figure


def add_target_threshold(
    figure: plotly.graph_objs.Figure,
    y_bottom: float,
    target_threshold_label: str | None,
    fill_colour: str = "rgba(135, 206, 235, 0.3)",
) -> plotly.graph_objs.Figure:
    """Add a blue bar with solid top line and dashed bottom line to a Plotly figure.

    Notes:
        The bar automatically spans the full width of the chart and extends to the top.
        For subplots, we draw a single continuous shape across the full figure width
        (xref="paper") so there are no gaps between subplots

    Args:
        figure: The Plotly figure object to add the threshold bar to
        y_bottom: Y-coordinate for the bottom of the bar (threshold value)
        fill_colour: Colour for the filled bar area (with transparency)
        target_threshold_label: Optional label for the threshold indicator

    Returns:
        The modified plotly figure object with the threshold bar added

    """
    line_color = "blue"

    # In cases where we let plotly figure out scaling, we have to compute the figure
    # and pull the y-axis range to tell us what the `y_top` value will be.
    computed_figure = figure.full_figure_for_development(warn=False)
    y_top: float = computed_figure.layout.yaxis.range[1]
    y_bottom = float(y_bottom)

    y_top = _round_to_significant_figure(number=y_top, significant_digits=3)

    # Solid top line
    figure.add_shape(
        type="line",
        xref="paper",
        x0=0,
        x1=1,
        yref="y",
        y0=y_top,
        y1=y_top,
        line={"color": line_color, "width": 2, "dash": "solid"},
        layer="above",
    )
    # Draw a single continuous rectangle across the full figure
    # using paper coords regardless of any breaks between subplots
    figure.add_shape(
        type="rect",
        xref="paper",
        x0=0,
        x1=1,
        yref="y",
        y0=y_bottom,
        y1=y_top,
        fillcolor=fill_colour,
        line={"width": 0},
        layer="above",
    )
    figure.add_shape(
        type="line",
        xref="paper",
        x0=0,
        x1=1,
        yref="y",
        y0=y_bottom,
        y1=y_bottom,
        line={"color": line_color, "width": 2, "dash": "dash"},
        layer="above",
    )

    if target_threshold_label:
        figure = _add_threshold_indicator(
            figure=figure,
            y_top=y_top,
            y_bottom=y_bottom,
            target_threshold_label=target_threshold_label,
        )

    return figure


def _add_threshold_indicator(
    *,
    figure: plotly.graph_objects.Figure,
    y_top: float,
    y_bottom: float,
    target_threshold_label: str,
):
    triangle_half_depth = 0.01
    triangle_half_height = y_top * triangle_half_depth
    triangle_x = 1

    figure.add_shape(
        type="path",
        path=(
            f"M {triangle_x} {y_bottom} "
            f"L {triangle_x + triangle_half_depth} {y_bottom + (triangle_half_height * 2)} "
            f"L {triangle_x + triangle_half_depth} {y_bottom - (triangle_half_height * 2)} Z"
        ),
        xref="paper",
        yref="y",
        fillcolor="black",
        line={"color": "black"},
        layer="above",
    )

    label_offset = 0.0025
    figure.add_annotation(
        xref="paper",
        x=triangle_x + triangle_half_depth + label_offset,
        yref="y",
        y=y_bottom,
        text=target_threshold_label,
        showarrow=False,
        font={"size": 10},
        xanchor="left",
        align="left",
    )
    return figure


def _round_to_significant_figure(*, number: float, significant_digits: int) -> float:
    return float(format(number, f".{significant_digits}g"))
