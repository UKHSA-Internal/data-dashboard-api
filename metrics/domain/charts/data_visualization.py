from typing import List, Union

import plotly.graph_objects
from django.db.models import Manager

from metrics.data.access.core_models import (
    get_hospital_admission_rates,
    get_vaccination_uptake_rates,
    get_weekly_disease_incidence,
)
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import line, line_with_shaded_section, waffle

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class ChartNotSupportedError(Exception):
    ...


def generate_corresponding_chart(topic: str, chart_type: str) -> str:
    chart_type = chart_type.lower()
    topic = topic.lower()

    if topic.lower() == "coronavirus":
        topic = "covid-19"

    if topic == "covid-19" and chart_type == "vaccinations":
        return create_waffle_chart_for_covid_vaccinations()

    if topic == "influenza":

        if chart_type == "healthcare":
            return (
                create_line_with_shaded_section_chart_for_influenza_hospitalisations()
            )

    if chart_type == "testing":
        return create_line_graph_with_shaded_section_for_weekly_positivity_by_age(
            topic=topic.title(),
        )

    raise ChartNotSupportedError()


def write_figure(
    figure: plotly.graph_objects.Figure, topic: str, file_format: str
) -> str:
    filename = f"{topic}.{file_format}"
    figure.write_image(file=filename, format=file_format)

    return filename


def create_basic_line_graph(
    topic: str,
    file_format: str,
) -> str:
    """For a given `topic`, queries the db, creates a basic line graph and writes the resulting file.

    Args:
        topic: The name of the topic. E.g. `Influenza`
        file_format: Can be any of the following:
            - 'png'
            - 'jpg' or 'jpeg'
            - 'webp'
            - 'svg'
            - 'pdf'

    Returns:
        str: The name of the file which has been written

    """
    weekly_disease_incidence: List[Union[int, float]] = get_weekly_disease_incidence(
        topic=topic,
    )
    figure: plotly.graph_objects.Figure = line.generate_chart_figure(
        data_points=weekly_disease_incidence
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_line_graph_with_shaded_section_for_weekly_positivity_by_age(
    topic: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    file_format: str = "png",
):
    dates, values = get_weekly_disease_incidence(
        topic=topic, core_time_series_manager=core_time_series_manager
    )

    figure: plotly.graph_objects.Figure = (
        line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name="weekly_hospital_admission_rate",
            rolling_period_slice=1,
        )
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_waffle_chart_for_covid_vaccinations(
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    file_format: str = "png",
):
    topic = "COVID-19"
    vaccine_doses: List[int] = get_vaccination_uptake_rates(
        topic="COVID-19", core_time_series_manager=core_time_series_manager
    )

    figure: plotly.graph_objects.Figure = waffle.generate_chart_figure(
        data_points=vaccine_doses
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_line_with_shaded_section_chart_for_influenza_hospitalisations(
    api_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    file_format: str = "png",
):
    topic = "Influenza"
    dates, values = get_hospital_admission_rates(
        topic=topic, core_time_series_manager=api_time_series_manager
    )

    figure: plotly.graph_objects.Figure = (
        line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name="weekly_hospital_admission_rate",
            rolling_period_slice=1,
        )
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)
