from typing import List

import plotly.graph_objects
from django.db.models import Manager

from metrics.data.access import core_models
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import line_with_shaded_section, waffle
from metrics.domain.charts.data_visualization import write_figure

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class ChartNotSupportedError(Exception):
    ...


def generate_corresponding_chart(topic: str, category: str, file_format: str) -> str:
    """
    Generate and return the chart for a given topic and category in the chosen file format

    Args:
        topic: The topic (eg. COVID-19) we want the chart for
        category: The required category (eg. cases, deaths) we want the chart for
        file_format: The required file format (eg svg, jpeg)

    Returns:
        The filename of the requested chart

    Raises:
        ChartNotSupportedError if there is no chart for the requested topic and category

    """
    category = category.lower()
    topic = topic.lower()

    if topic.lower() == "coronavirus":
        topic = "covid-19"

    if topic == "covid-19":
        if category == "vaccinations":
            return create_waffle_chart_for_covid_vaccinations(file_format=file_format)
        if category == "cases":
            return create_line_with_shaded_section_chart_for_covid_cases(
                file_format=file_format
            )
        if category == "deaths":
            return create_line_with_shaded_section_chart_for_covid_deaths(
                file_format=file_format
            )

    if topic == "influenza":
        if category == "healthcare":
            return create_line_with_shaded_section_chart_for_influenza_hospitalisations(
                file_format=file_format
            )

        if category == "testing":
            return create_line_graph_with_shaded_section_for_weekly_positivity_by_age(
                topic=topic.title(),
                file_format=file_format,
            )

    raise ChartNotSupportedError()

def create_line_graph_with_shaded_section_for_weekly_positivity_by_age(
    topic: str,
    file_format: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> str:
    """
    Create a line graph for the weekly_positivity metric

    Args:
        topic: The required topic (eg. COVID-19)
        file_format: The required file format (eg svg, jpeg)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The filename of the graph
    """

    metric_name = "weekly_positivity"
    dates, values = core_models.get_timeseries_metric_values_from_date(
        topic=topic,
        metric_name=metric_name,
        core_time_series_manager=core_time_series_manager,
    )

    change_in_metric_value = core_models.get_metric_value(
        metric_name="weekly_percent_change_positivity",
        topic=topic,
    )

    figure: plotly.graph_objects.Figure = (
        line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name=metric_name,
            change_in_metric_value=change_in_metric_value,
            rolling_period_slice=1,
        )
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_waffle_chart_for_covid_vaccinations(
    file_format: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> str:
    """
    Create a COVID-19 waffle chart

    Args:
        file_format: The required file format (eg svg, jpeg)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The filename of the chart
    """

    topic = "COVID-19"
    vaccine_doses: List[int] = core_models.get_vaccination_uptake_rates(
        topic="COVID-19", core_time_series_manager=core_time_series_manager
    )

    figure: plotly.graph_objects.Figure = waffle.generate_chart_figure(
        data_points=vaccine_doses
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_line_with_shaded_section_chart_for_influenza_hospitalisations(
    file_format: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> str:
    """
    Create an Influenza line chart for weekly_hospital_admissions_rate

    Args:
        file_format: The required file format (eg svg, jpeg)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The filename of the chart
    """

    topic = "Influenza"
    metric_name = "weekly_hospital_admissions_rate"

    dates, values = core_models.get_timeseries_metric_values_from_date(
        topic=topic,
        metric_name=metric_name,
        core_time_series_manager=core_time_series_manager,
    )

    change_in_metric_value = core_models.get_metric_value(
        metric_name="weekly_hospital_admissions_rate_change_percentage",
        topic=topic,
    )

    figure: plotly.graph_objects.Figure = (
        line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name=metric_name,
            change_in_metric_value=change_in_metric_value,
            rolling_period_slice=1,
        )
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_line_with_shaded_section_chart_for_covid_cases(
    file_format: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> str:
    """
    Create a COVID-19 line chart for new_cases_daily

    Args:
        file_format: The required file format (eg svg, jpeg)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The filename of the chart
    """

    topic = "COVID-19"
    metric_name = "new_cases_daily"

    dates, values = core_models.get_timeseries_metric_values_from_date(
        topic=topic,
        metric_name=metric_name,
        core_time_series_manager=core_time_series_manager,
    )

    change_in_metric_value = core_models.get_metric_value(
        metric_name="new_cases_7days_change_percentage",
        topic=topic,
    )

    figure: plotly.graph_objects.Figure = (
        line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name=metric_name,
            change_in_metric_value=change_in_metric_value,
            rolling_period_slice=7,
        )
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)


def create_line_with_shaded_section_chart_for_covid_deaths(
    file_format: str,
    core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
) -> str:
    """
    Create a COVID-19 line chart for new_deaths_daily

    Args:
        file_format: The required file format (eg svg, jpeg)
        core_time_series_manager: The timeseries manager. Default is the CoreTimeSeries manager

    Returns:
        The filename of the chart
    """

    topic = "COVID-19"
    metric_name = "new_deaths_daily"

    dates, values = core_models.get_timeseries_metric_values_from_date(
        topic=topic,
        metric_name=metric_name,
        core_time_series_manager=core_time_series_manager,
    )

    change_in_metric_value = core_models.get_metric_value(
        metric_name="new_deaths_7days_change_percentage",
        topic=topic,
    )

    figure: plotly.graph_objects.Figure = (
        line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name=metric_name,
            change_in_metric_value=change_in_metric_value,
            rolling_period_slice=7,
        )
    )

    return write_figure(figure=figure, topic=topic, file_format=file_format)
