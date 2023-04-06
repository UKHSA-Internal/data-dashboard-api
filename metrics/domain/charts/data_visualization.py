import datetime

import plotly.graph_objects

from metrics.data.models.core_models import CoreTimeSeries
from metrics.interfaces.charts.access import ChartsInterface

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


def generate_chart(
    topic: str,
    metric: str,
    chart_type: str,
    date_from,
):
    date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
    library = ChartsInterface(
        topic=topic, metric=metric, chart_type=chart_type, date_from=date_from
    )
    figure = library.generate_chart_figure()

    return write_figure(figure=figure, topic=f"{topic}.{metric}", file_format="png")


def write_figure(
    figure: plotly.graph_objects.Figure, topic: str, file_format: str
) -> str:
    """
    Convert a figure to a static image and write to a file in the desired image format

    Args:
        figure: The figure object or a dictioanry representing a figure
        topic: The required topic (eg. COVID-19)
        file_format: The required file format (eg svg, jpeg)

    Returns:
        The filename of the image
    """

    filename = f"{topic}.{file_format}"
    figure.write_image(file=filename, format=file_format)

    return filename
