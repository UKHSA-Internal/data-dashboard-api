import datetime

import pytest
from wagtail.models import Page

from cms.home.models import HomePage
from metrics.domain.models import PlotData, PlotParameters, PlotsCollection
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
        date_to="2023-12-31",
        x_axis="date",
        y_axis="metric",
    )


@pytest.fixture
def fake_plots_collection(
    fake_chart_plot_parameters: PlotParameters,
) -> PlotsCollection:
    return PlotsCollection(
        plots=[fake_chart_plot_parameters],
        file_format="svg",
        chart_width=930,
        chart_height=220,
        x_axis="date",
        y_axis="metric",
    )


@pytest.fixture
def fake_chart_plot_parameters_covid_cases() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
        date_from="2023-01-01",
        date_to="2023-12-31",
    )


@pytest.fixture
def valid_plot_parameters() -> PlotParameters:
    return PlotParameters(
        metric="COVID-19_deaths_ONSByDay",
        topic="COVID-19",
        chart_type=ChartTypes.line_multi_coloured.value,
        date_from="2023-01-01",
        date_to="2023-12-31",
        x_axis="date",
        y_axis="metric",
    )


@pytest.fixture
def fake_plot_data() -> PlotData:
    plot_params = PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
        x_axis="metric",
        y_axis="date",
    )
    y_axis_values = [1, 2, 4, 5, 5, 2, 1]
    return PlotData(
        parameters=plot_params,
        x_axis_values=[
            datetime.date(year=2023, month=1, day=i + 1)
            for i in range(len(y_axis_values))
        ],
        y_axis_values=y_axis_values,
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
def example_headline_data() -> dict[str, str | list[dict[str, str | float]]]:
    return {
        "parent_theme": "infectious_disease",
        "child_theme": "respiratory",
        "topic": "RSV",
        "metric_group": "headline",
        "metric": "RSV_headline_positivityLatest",
        "geography_type": "Nation",
        "geography": "England",
        "geography_code": "E92000001",
        "age": "all",
        "sex": "all",
        "stratum": "default",
        "data": [
            {
                "period_start": "2023-10-15",
                "period_end": "2023-10-22",
                "metric_value": 12.3,
                "embargo": "2023-11-16 17:30:00",
            },
            {
                "period_start": "2023-10-23",
                "period_end": "2023-10-30",
                "metric_value": 10.7,
                "embargo": "2023-11-16 17:30:00",
            },
        ],
        "refresh_date": "2023-11-09",
    }


@pytest.fixture
def example_time_series_data() -> dict[str, str | list[dict[str, str | float]]]:
    return {
        "parent_theme": "infectious_disease",
        "child_theme": "respiratory",
        "topic": "COVID-19",
        "metric_group": "cases",
        "metric": "COVID-19_cases_countRollingMean",
        "geography_type": "Nation",
        "geography": "England",
        "geography_code": "E92000001",
        "age": "all",
        "sex": "all",
        "stratum": "default",
        "metric_frequency": "daily",
        "refresh_date": "2023-11-20",
        "time_series": [
            {
                "epiweek": 44,
                "date": "2022-11-01",
                "metric_value": 4141.43,
                "embargo": "2023-11-16 17:30:00",
            },
            {
                "epiweek": 44,
                "date": "2022-11-02",
                "metric_value": 3952.14,
                "embargo": "2023-11-16 17:30:00",
            },
        ],
    }


@pytest.fixture
def dashboard_root_page() -> HomePage:
    root_page = HomePage(
        title="UKHSA Dashboard Root",
        slug="ukhsa-dashboard-root",
    )

    wagtail_root_page = Page.get_first_root_node()
    root_page = wagtail_root_page.add_child(instance=root_page)
    wagtail_root_page.save_revision().publish()

    root_page.save_revision().publish()
    return root_page


@pytest.fixture
def example_chart_block() -> dict[str, str | list[dict]]:
    return {
        "title": "Admissions rate by age",
        "body": "Age breakdown of people admitted to hospital.",
        "x_axis": "stratum",
        "y_axis": "metric",
        "chart": [
            {
                "type": "plot",
                "value": {
                    "topic": "COVID-19",
                    "metric": "COVID-19_healthcare_admissionByDay",
                    "chart_type": "bar",
                    "date_from": None,
                    "date_to": None,
                    "stratum": "",
                    "geography": "England",
                    "geography_type": "Nation",
                    "sex": "",
                    "age": "",
                    "label": "Admission rate",
                    "line_colour": "",
                    "line_type": "",
                },
                "id": "791efbf1-8880-4dfa-9f5d-526982ed1539",
            }
        ],
    }


@pytest.fixture
def example_headline_number_block() -> dict[str, str]:
    return {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
        "geography": "Croydon",
        "geography_type": "Upper Tier Local Authority",
        "sex": "all",
        "age": "all",
        "stratum": "default",
        "body": "Last 7 days",
    }


@pytest.fixture
def example_trend_number_block() -> dict[str, str]:
    return {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayChange",
        "body": "Last 7 days",
        "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
        "geography": "England",
        "geography_type": "Nation",
        "sex": "all",
        "age": "all",
        "stratum": "default",
    }
