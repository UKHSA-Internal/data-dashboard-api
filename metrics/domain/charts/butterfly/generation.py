from collections import defaultdict

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.dual_category import DualCategoryChartSettings
from metrics.domain.models import ChartGenerationPayload


def generate_butterfly(
    *,
    chart_generation_payload: ChartGenerationPayload,
) -> go.Figure:

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

    figure = make_subplots(
        rows = 1,
        cols = 2,
        shared_xaxes=True,
        shared_yaxes=True,
        horizontal_spacing=0.01,
        subplot_titles=("title 1", "title 2")
    )

    figure.add_trace(
        go.bar
    )

    return figure