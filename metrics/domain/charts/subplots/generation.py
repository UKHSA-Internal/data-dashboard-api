import math

import plotly.graph_objects
from plotly.subplots import make_subplots

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.chart_settings.subplot_chart_settings import (
    SubplotChartSettings,
)
from metrics.domain.models import PlotGenerationData
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload


def format_legend_names(
    figure: plotly.graph_objects.Figure,
) -> plotly.graph_objects.Figure:
    plot_labels = set()

    for plot in figure.data:
        name = plot.name
        plot.legendgroup = name
        plot.showlegend = name not in plot_labels
        plot_labels.add(name)

    return figure


def generate_chart_figure(
    *,
    chart_generation_payload: SubplotChartGenerationPayload,
) -> plotly.graph_objects.Figure:
    subplot_data: PlotGenerationData = chart_generation_payload.subplot_data
    settings = SubplotChartSettings(
        chart_generation_payload=chart_generation_payload,
    )

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
            ticktext=[plot_data.subplot_title],
            tickvals=[math.ceil(len(plot_data.subplot_data) / 2) - 1],
        )

    figure.update_layout(**settings.get_subplot_chart_config())
    figure.update_yaxes(**settings.get_subplot_yaxis_config())
    figure.update_xaxes(**settings.get_subplot_xaxis_config())

    # Update primary y-axis settings (first subplot)
    figure.update_yaxes(**settings.get_primary_subplot_yaxis_config())

    return format_legend_names(figure=figure)
