import plotly.graph_objects

from data.access import get_weekly_disease_incidence
from domain.charts.generation import generate_chart_figure


def generate_chart_for_topic(
    topic: str, metric: str, year: int = 2022
):
    weekly_disease_incidence = get_weekly_disease_incidence(
        topic=topic,
        metric=metric,
        year=year,
    )
    return generate_chart_figure(data_points=weekly_disease_incidence)


def generate_svg_chart_for_topic(
    topic: str, metric: str = "weekly_positivity", year: int = 2022
):
    figure = generate_chart_for_topic(topic=topic, metric=metric, year=year)
    return write_figure(figure=figure, topic=topic)


def write_figure(figure: plotly.graph_objects.Figure, topic: str) -> str:

    filename = f"{topic}.png"
    figure.write_image(file=filename, format="png")

    return filename
