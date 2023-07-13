import datetime

import pytest

from metrics.domain.models import PlotParameters
from metrics.domain.utils import ChartTypes
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager

DATA_PAYLOAD_HINT = dict[str, str | datetime.date]


@pytest.fixture
def fake_chart_plot_parameters() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="COVID-19_testing_7daypositivity",
        stratum="default",
        date_from="2023-01-01",
        x_axis="date",
        y_axis="metric",
    )


@pytest.fixture
def fake_chart_plot_parameters_covid_cases() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
    )


@pytest.fixture
def valid_plot_parameters() -> PlotParameters:
    return PlotParameters(
        metric="COVID-19_deaths_ONSByDay",
        topic="COVID-19",
        chart_type=ChartTypes.simple_line.value,
        date_from="2022-01-01",
        x_axis="date",
        y_axis="metric",
    )


@pytest.fixture
def fake_password_prefix() -> str:
    return "ag619m16"


@pytest.fixture
def fake_password_suffix() -> str:
    return "16ui27iu26ui236827io26897yvbn19d"


@pytest.fixture
def plot_serializer_payload_and_model_managers() -> (
    tuple[DATA_PAYLOAD_HINT, FakeMetricManager, FakeTopicManager]
):
    fake_metric = FakeMetricFactory.build_example_metric()
    fake_topic = fake_metric.metric_group.topic

    data: DATA_PAYLOAD_HINT = {
        "topic": fake_topic.name,
        "metric": fake_metric.name,
        "chart_type": ChartTypes.line_with_shaded_section.value,
    }

    return data, FakeMetricManager([fake_metric]), FakeTopicManager([fake_topic])


@pytest.fixture
def example_headline_data_json() -> list[dict[str, str | float]]:
    return [
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "headline",
            "metric": "COVID-19_headline_positivity_latest",
            "geography_type": "Lower Tier Local Authority",
            "geography": "Babergh",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "period_start": "2023-06-05",
            "period_end": "2023-06-11",
            "metric_value": 0.087,
            "refresh_date": "2023-06-21",
        },
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "headline",
            "metric": "COVID-19_headline_positivity_latest",
            "geography_type": "UKHSA Region",
            "geography": "Yorkshire and Humber",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "period_start": "2023-06-05",
            "period_end": "2023-06-11",
            "metric_value": 0.0639,
            "refresh_date": "2023-06-21",
        },
    ]


@pytest.fixture
def example_timeseries_data_json() -> list[dict[str, str | float]]:
    return [
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "deaths",
            "metric": "COVID-19_deaths_ONSByDay",
            "geography_type": "Nation",
            "geography": "England",
            "geography_code": "E92000001",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "metric_frequency": "daily",
            "epiweek": 10,
            "month": 3,
            "year": 2020,
            "date": "2020-03-02",
            "metric_value": 0,
            "refresh_date": "2023-07-11"
        },
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "deaths",
            "metric": "COVID-19_deaths_ONSByDay",
            "geography_type": "Nation",
            "geography": "England",
            "geography_code": "E92000001",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "metric_frequency": "daily",
            "epiweek": 10,
            "month": 3,
            "year": 2020,
            "date": "2020-03-03",
            "metric_value": 0,
            "refresh_date": "2023-07-11"
        },
    ]
