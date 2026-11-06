import plotly.graph_objects as go

from collections import defaultdict

from plotly.graph_objs import Bar
from plotly.subplots import make_subplots

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.dual_category import DualCategoryChartSettings
from metrics.domain.models.plots import ChartGenerationPayload


def generate_butterfly(
    *,
    chart_generation_payload: ChartGenerationPayload,
):
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

    figure = go.Figure()

    values = []
    column = 0
    keys = [key for i, key in enumerate(grouped) if i < 2]
    for key in keys:
        x_values = grouped[key]["x_axis_values"]
        if column < 1:
            original = grouped[key]["x_axis_values"]
            x_values = [-x for x in original]
        figure.add_trace(
            go.Bar(
                x=x_values,
                y=grouped[key]["y_axis_values"],
                orientation='h',
                name=grouped[key]["label"],
                marker_color=grouped[key]["colour"],
            )
        )
        column += 1
        values.extend([grouped[key]["x_axis_values"]])

    layout_args = settings.get_butterfly_chart_config(values[0], values[1])
    figure.update_layout(**layout_args)

    return figure