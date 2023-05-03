from metrics.domain.models import ChartPlotData


def get_label_from_plot_data(plot_data: ChartPlotData) -> str:
    """Returns a label used for the plot legend based on the params within the `plot_data` model

    Args:
        plot_data: A `ChartPlotData` model containing
            the associated params for the chart plots

    Returns:
        str: A label which can be used for the chart
            plot on the legend of the chart figure

    """
    stratum: str = plot_data.parameters.stratum

    if not stratum:
        return f"{plot_data.parameters.topic}:{plot_data.parameters.metric}"

    return stratum
