import plotly.graph_objects

from data.access.api_models import get_weekly_disease_incidence
from domain.charts.generation import generate_chart_figure


def create_chart_figure_for_topic(
    topic: str, metric: str, year: int = 2022
) -> plotly.graph_objects.Figure:
    weekly_disease_incidence = get_weekly_disease_incidence(
        topic=topic,
        metric=metric,
        year=year,
    )
    return generate_chart_figure(data_points=weekly_disease_incidence)


def write_chart_file_for_topic(
    topic: str,
    metric: str = "weekly_positivity",
    year: int = 2022,
    file_format: str = "svg",
) -> str:
    """For a given `topic`, queries the db, creates a chart and writes the resulting file.

    Args:
        topic: The name of the topic. E.g. `Influenza`
        metric: The metric to create the chart for.
            Defaults to "weekly_positivity"
        year: The year to generate the chart data for.
            Defaults to 2022
        file_format: Can be any of the following:
            - 'png'
            - 'jpg' or 'jpeg'
            - 'webp'
            - 'svg'
            - 'pdf'
            Defaults to `svg`

    Returns:
        str: The name of the file which has been written

    """
    figure: plotly.graph_objects.Figure = create_chart_figure_for_topic(
        topic=topic, metric=metric, year=year
    )
    return write_figure(figure=figure, topic=topic, file_format=file_format)


def write_figure(
    figure: plotly.graph_objects.Figure, topic: str, file_format: str
) -> str:

    filename = f"{topic}.{file_format}"
    figure.write_image(file=filename, format=file_format)

    return filename
