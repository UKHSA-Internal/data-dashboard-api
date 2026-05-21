from collections import defaultdict

import plotly.graph_objects as go

from metrics.domain.models.plots import ChartGenerationPayload


def generate_stacked_bar(
    *,
    chart_generation_payload: ChartGenerationPayload,
):
    """"""
    figure = go.Figure()

    grouped: dict[str, dict] = defaultdict(
        lambda: {"x_axis_values": [], "y_axis_values": []}
    )

    secondary_category = chart_generation_payload.secondary_category
    for plot in chart_generation_payload.plots:
        group = plot.parameters.model_dump()[secondary_category]
        grouped[group]["x_axis_values"].extend(plot.x_axis_values)
        grouped[group]["y_axis_values"].extend(plot.y_axis_values)

    for label, data in grouped.items():
        figure.add_trace(
            go.Bar(
                x=data["x_axis_values"],
                y=data["y_axis_values"],
                name=label,
            )
        )

    figure.update_layout({"xaxis": {"type": "category"}}, barmode="stack")

    return figure
