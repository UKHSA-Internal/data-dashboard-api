import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.subplot_chart_settings import SubplotChartSettings
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload, SubplotGenerationData


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


def format_legend_names(figure: go.Figure) -> tuple[go.Figure, set[str]]:
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
) -> go.Figure:
    settings = SubplotChartSettings(
        chart_generation_payload=chart_generation_payload,
    )
    subplot_data: list[SubplotGenerationData] = chart_generation_payload.subplot_data

    figure = make_subplots(**settings.get_make_subplots_config())
    chart_orientation = "v" if settings.is_horizontal_chart else "h"

    for plot_index, plot_data in enumerate(subplot_data, start=1):

        rows, cols = (1, plot_index) if settings.is_horizontal_chart else (plot_index, 1)

        for data in plot_data.subplot_data:

            x_values, y_values = (
                (data.x_axis_values, data.y_axis_values)
                if settings.is_horizontal_chart
                else (data.y_axis_values, data.x_axis_values)
            )

            figure.add_trace(
                go.Bar(
                    x=x_values,
                    y=y_values,
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
                    orientation=chart_orientation,
                ),
                row=rows,
                col=cols,
            )

        """
        Review the docs for this - is this the chart or subplot and what implications does
        this have for the `col` property?
        """
        axis_config = {
            "col":plot_index,
            "ticktext":[format_tick_text(tick_text=plot_data.subplot_title)],
            "tickvals":[math.ceil(len(plot_data.subplot_data) / 2) - 1],
        }

        if settings.is_horizontal_chart:
            figure.update_xaxes(**axis_config)

        if not settings.is_horizontal_chart:
            figure.update_yaxes(**axis_config)

    [figure, plot_labels] = format_legend_names(figure)

    """
    This section needs work on how to apply these correctly
    This updates the styles for the chart (background colour, grid etc)
    and the plot labels updates converting y or x axis labels to the correct titles
    depending on the "orientation"

    currently just switch which xxis config loaded into x or y, this should be cleaned up
    (probably in settings).

    """
    figure.update_layout(
        **settings.get_subplot_chart_config(number_of_legend_items=len(plot_labels))
    )
    if settings.is_horizontal_chart:
        figure.update_yaxes(**settings.get_subplot_yaxis_config())
        figure.update_xaxes(**settings.get_subplot_xaxis_config())

    if not settings.is_horizontal_chart:
        figure.update_yaxes(**settings.get_subplot_xaxis_config())
        figure.update_xaxes(**settings.get_subplot_yaxis_config())

    ## Update primary y-axis settings (first subplot)

    if settings.is_horizontal_chart:
        figure.update_yaxes(**settings.get_primary_subplot_yaxis_config())

    if not settings.is_horizontal_chart:
        figure.update_xaxes(**settings.get_primary_subplot_yaxis_config())

    figure.update_layout(**settings.get_x_axis_title_as_annotation_config())

    if chart_generation_payload.target_threshold and settings.is_horizontal_chart:
        figure = add_target_threshold(
            figure=figure,
            y_bottom=chart_generation_payload.target_threshold,
            target_threshold_label=chart_generation_payload.target_threshold_label,
        )

    if chart_generation_payload.target_threshold and settings.is_horizontal_chart:
        pass

    return figure


def add_target_threshold(
    figure: go.Figure,
    y_bottom: float,
    target_threshold_label: str | None,
    fill_colour: str = "rgba(135, 206, 235, 0.3)",
) -> go.Figure:
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
    figure: go.Figure,
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
