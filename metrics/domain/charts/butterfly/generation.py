import plotly.graph_objects as go

from metrics.domain.charts.chart_settings.dual_category import DualCategoryChartSettings
from metrics.domain.charts.utils import (
    extract_grouped_data_from_chart_generation_payload,
)
from metrics.domain.models.plots import ChartGenerationPayload

BUTTERFLY_LIMIT = 2


def generate_butterfly(
    *,
    chart_generation_payload: ChartGenerationPayload,
):
    """
    Generates a butterfly chart.

    Args:
        chart_generation_payload: The payload for the chart generation.

    Returns:
        The figure for the butterfly chart.
    """
    settings = DualCategoryChartSettings(
        chart_generation_payload=chart_generation_payload,
    )

    grouped = extract_grouped_data_from_chart_generation_payload(
        chart_generation_payload=chart_generation_payload
    )

    figure = go.Figure()

    values = []

    keys = [key for i, key in enumerate(grouped) if i < BUTTERFLY_LIMIT]
    for column, key in enumerate(keys):
        x_values = grouped[key]["x_axis_values"]
        if column < 1:
            original = grouped[key]["x_axis_values"]
            x_values = [-x for x in original]
        figure.add_trace(
            go.Bar(
                x=x_values,
                y=grouped[key]["y_axis_values"],
                orientation="h",
                name=grouped[key]["label"],
                marker_color=grouped[key]["colour"],
            )
        )
        values.extend([grouped[key]["x_axis_values"]])

    layout_args = settings.get_butterfly_chart_config(values[0], values[1])
    figure.update_layout(**layout_args)

    return figure
