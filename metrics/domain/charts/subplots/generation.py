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

    return figure
