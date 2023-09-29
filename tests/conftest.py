import datetime

import pytest
from rest_framework.test import APIClient
from rest_framework_api_key.models import APIKey

from ingestion.data_transfer_models import IncomingHeadlineDTO
from ingestion.data_transfer_models.incoming import IncomingTimeSeriesDTO
from metrics.domain.models import PlotData, PlotParameters
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
        metric="COVID-19_testing_positivity7DayRolling",
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
def fake_chart_plots_data() -> PlotData:
    plot_params = PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
        x_axis="metric",
        y_axis="date",
    )
    x_values = [1, 2, 4, 5, 5, 2, 1]
    return PlotData(
        parameters=plot_params,
        x_axis_values=[1, 2, 4, 5, 5, 2, 1],
        y_axis_values=[
            datetime.date(year=2023, month=1, day=i + 1) for i in range(len(x_values))
        ],
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
def example_headline_data() -> list[dict[str, str | float]]:
    return [
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "headline",
            "metric": "COVID-19_headline_ONSdeaths_7DayChange",
            "geography_type": "Government Office Region",
            "geography": "East Midlands",
            "geography_code": "E12000004",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "period_start": "2023-06-24",
            "period_end": "2023-06-30",
            "metric_value": 1,
            "refresh_date": "2023-07-11",
        },
        {
            "parent_theme": "infectious_disease",
            "child_theme": "respiratory",
            "topic": "COVID-19",
            "metric_group": "headline",
            "metric": "COVID-19_headline_ONSdeaths_7DayChange",
            "geography_type": "Government Office Region",
            "geography": "East of England",
            "geography_code": "E12000006",
            "age": "all",
            "sex": "all",
            "stratum": "default",
            "period_start": "2023-06-24",
            "period_end": "2023-06-30",
            "metric_value": -11,
            "refresh_date": "2023-07-11",
        },
    ]


@pytest.fixture
def example_incoming_headline_dto(
    example_headline_data: list[dict[str, str | float]]
) -> IncomingHeadlineDTO:
    return IncomingHeadlineDTO(**example_headline_data[0])


@pytest.fixture
def example_timeseries_data() -> list[dict[str, str | int | float]]:
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
            "refresh_date": "2023-07-11",
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
            "refresh_date": "2023-07-11",
        },
    ]


@pytest.fixture
def example_incoming_timeseries_dto(
    example_timeseries_data: list[dict[str, str | float]]
) -> IncomingTimeSeriesDTO:
    return IncomingTimeSeriesDTO(**example_timeseries_data[0])


@pytest.fixture
def authenticated_api_client() -> APIClient:
    _, key = APIKey.objects.create_key(name="Test Key")

    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=key)

    return api_client
