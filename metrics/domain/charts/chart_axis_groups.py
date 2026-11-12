from metrics.domain.common.utils import ChartTypes

X_DOMINANT_CHARTS = [
    ChartTypes.stacked_bar.value,
]

Y_DOMINANT_CHARTS = [
    ChartTypes.butterfly.value,
]

def pick_axis(chart_type, x, y):
    if chart_type in X_DOMINANT_CHARTS:
        return x
    if chart_type in Y_DOMINANT_CHARTS:
        return y
    # Raise value error as chart type not recognised
    raise ValueError(f"Unknown chart type {chart_type}")