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

    figure = make_subplots(
        rows=1,
        cols=2,
        shared_xaxes=True,
        shared_yaxes=True,
        horizontal_spacing=0
    )

    column = 1
    values = []
    keys = [key for i, key in enumerate(grouped) if i < 2]
    for key in keys:
        figure.add_trace(
            go.Bar(
                x=grouped[key]["x_axis_values"],
                y=grouped[key]["y_axis_values"],
                orientation='h',
                name=grouped[key]["label"],
                marker_color=grouped[key]["colour"],
                # hovertemplate="%{y}<extra></extra>",
            ),
            row=1,
            col=column
        )
        column += 1
        values.extend([grouped[key]["x_axis_values"]])

    figure.update_xaxes(autorange="reversed", row=1, col=1)

    max_val = float(max(max(values[0]), max(values[1]))) * 1.1
    figure.update_xaxes(range=[0, max_val], row=1, col=1)
    figure.update_xaxes(range=[0, max_val], row=1, col=2)
    figure.update_yaxes(type="category")

    # layout_args = settings.get_stacked_bar_chart_config()
    # figure.update_layout(**layout_args)

    # figure.update_layout(
    #     title_x=0.5,
    #     barmode="overlay",
    #     bargap=0.2,
    #     showlegend=False,
    #     width=800,
    #     height=500
    # )

    return figure