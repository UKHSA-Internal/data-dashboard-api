from metrics.domain.common.utils import ChartTypes

X_DOMINANT_CHARTS = [
    ChartTypes.stacked_bar.value,
]

Y_DOMINANT_CHARTS = [
    ChartTypes.butterfly.value,
]


def pick_axis(chart_type, x_dominant, y_dominant):
    if chart_type in X_DOMINANT_CHARTS:
        return x_dominant
    if chart_type in Y_DOMINANT_CHARTS:
        return y_dominant
    raise ValueError


def resolve_axis(chart_type, x_dominant, y_dominant):
    if chart_type in X_DOMINANT_CHARTS:
        return x_dominant
    if chart_type in Y_DOMINANT_CHARTS:
        return y_dominant
    return x_dominant
