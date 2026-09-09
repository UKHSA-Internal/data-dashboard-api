from collections import defaultdict

import plotly.graph_objects as go

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.dual_category import DualCategoryChartSettings
from metrics.domain.charts.reporting_delay_period import add_reporting_delay_period
from metrics.domain.models.plots import ChartGenerationPayload


def generate_stacked_bar(
    *,
    chart_generation_payload: ChartGenerationPayload,
):
    """
    Generates a stacked bar chart.

    Args:
        chart_generation_payload: The payload for the chart generation.

    Returns:
        The figure for the stacked bar chart.
    """
    figure = go.Figure()
    settings = DualCategoryChartSettings(
        chart_generation_payload=chart_generation_payload,
    )

    grouped: dict[str, dict] = defaultdict(
        lambda: {"x_axis_values": [], "y_axis_values": []}
    )

    secondary_category = chart_generation_payload.secondary_category
    for plot in chart_generation_payload.plots:
        selected_colour: colour_scheme.RGBAChartLineColours = (
            colour_scheme.RGBAChartLineColours.get_colour(
                colour=plot.parameters.line_colour
            )
        )
        group = getattr(plot.parameters, secondary_category)
        grouped[group]["x_axis_values"].extend(plot.x_axis_values)
        grouped[group]["y_axis_values"].extend(plot.y_axis_values)
        grouped[group]["label"] = plot.parameters.label
        grouped[group]["colour"] = selected_colour.stringified

    for label, data in grouped.items():
        figure.add_trace(
            go.Bar(
                x=data["x_axis_values"],
                y=data["y_axis_values"],
                name=data["label"] or label,
                marker={
                    "color": data["colour"],
                },
            )
        )

    if settings.is_date_type_x_axis:
        add_reporting_delay_period(
            chart_plots_data=chart_generation_payload.plots,
            figure=figure,
        )

    layout_args = settings.get_stacked_bar_chart_config()
    figure.update_layout(**layout_args)

    return figure
