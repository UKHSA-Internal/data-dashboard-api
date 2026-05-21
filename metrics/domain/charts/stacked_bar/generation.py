import plotly.graph_objects as go

from metrics.domain.models import PlotGenerationData


def create_stacked_bar_chart(
    *,
    chart_generation_payload,
):
    """"""
    figure = go.Figure()