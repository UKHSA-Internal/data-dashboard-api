import datetime
from decimal import Decimal
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from wagtail.models import Page
from wagtail.models.i18n import Locale

from cms.home.models.home_page import UKHSARootPage
from metrics.domain.models import (
    PlotGenerationData,
    PlotParameters,
    ChartRequestParams,
)
from metrics.domain.common.utils import ChartTypes
from metrics.domain.models.charts.subplot_charts import (
    SubplotChartRequestParameters,
    Subplots,
)
from metrics.domain.models.subplot_plots import (
    SubplotChartGenerationPayload,
    SubplotGenerationData,
)
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.topic_manager import FakeTopicManager

DATA_PAYLOAD_HINT = dict[str, str | datetime.date]


@pytest.fixture
def example_subplot_chart_generation_payload() -> list[dict[str, str | Decimal]]:
    return [
        {
            "subplot_title": "6-in-1",
            "subplot_data": [
                {
                    "parameters": {
                        "metric": "fake-metric",
                        "topic": "fake-topic",
                        "geography": "Darlington",
                    },
                    "x_axis_values": ["Darlington"],
                    "y_axis_values": [Decimal("95.4")],
                },
                {
                    "parameters": {
                        "metric": "fake-metric",
                        "topic": "fake-topic",
                        "geography": "Hartlepool",
                    },
                    "x_axis_values": ["Hartlepool"],
                    "y_axis_values": [Decimal("93.4")],
                },
                {
                    "parameters": {
                        "metric": "fake-metric",
                        "topic": "fake-topic",
                        "geography": "Stockton-on-Tees",
                    },
                    "x_axis_values": ["Stockton-on-Tees"],
                    "y_axis_values": [Decimal("95.4")],
                },
            ],
        },
        {
            "subplot_title": "MMR1",
            "subplot_data": [
                {
                    "parameters": {
                        "metric": "fake-metric-two",
                        "topic": "fake-topic-two",
                        "geography": "Darlington",
                    },
                    "x_axis_values": ["Darlington"],
                    "y_axis_values": [Decimal("92.4")],
                },
                {
                    "parameters": {
                        "metric": "fake-metric-two",
                        "topic": "fake-topic-two",
                        "geography": "Hartlepool",
                    },
                    "x_axis_values": ["Hartlepool"],
                    "y_axis_values": [Decimal("91.4")],
                },
                {
                    "parameters": {
                        "metric": "fake-metric",
                        "topic": "fake-topic",
                        "geography": "Stockton-on-Tees",
                    },
                    "x_axis_values": ["Stockton-on-Tees"],
                    "y_axis_values": [Decimal("95.4")],
                },
            ],
        },
    ]


def create_subplots_data() -> list[Subplots]:
    subplots: list[Subplots] = []
    plots: list[PlotParameters] = []

    for i in range(2):
        plots.append(
            PlotParameters(
                chart_type="bar",
                topic="COVID-19",
                metric="COVID-19_testing_positivity7DayRolling",
                stratum="default",
                date_from="2023-01-01",
                date_to="2023-12-31",
                x_axis="date",
                y_axis="metric",
            )
        )

    for i in range(1, 3):
        subplots.append(
            Subplots(
                subplot_title=f"Subplot {i}",
                x_axis="Geography",
                y_axis="Metric",
                plots=plots,
            )
        )

    return subplots


@pytest.fixture
def fake_subplot_chart_generation_payload() -> SubplotChartGenerationPayload:
    return SubplotChartGenerationPayload(
        subplot_data=[],
        chart_width=600,
        chart_height=200,
        x_axis_title="x axis title",
        y_axis_title="y axis title",
        y_axis_minimum_value=0,
        y_axis_maximum_value=None,
    )


@pytest.fixture
def fake_subplot_chart_request_params() -> SubplotChartRequestParameters:
    return SubplotChartRequestParameters(
        file_format="svg",
        chart_width=930,
        chart_height=220,
        x_axis_title="x axis title",
        y_axis_title="y axis title",
        y_axis_minimum_value=0,
        y_axis_maximum_value=None,
        subplots=create_subplots_data(),
    )


@pytest.fixture
def fake_subcategory_choices_grouped_by_categories() -> dict[str, list[str]]:
    return {
        "age": ["00-04", "05-11"],
        "sex": ["m", "f"],
        "stratum": ["default", "unknown"],
        "geography": {
            "Nation": ["England", "England"],
            "Region": ["RegionOne", "RegionOne"],
        },
    }


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
def fake_chart_request_params(
    fake_chart_plot_parameters: PlotParameters,
) -> ChartRequestParams:
    return ChartRequestParams(
        plots=[fake_chart_plot_parameters],
        file_format="svg",
        chart_width=930,
        chart_height=220,
        x_axis="date",
        y_axis="metric",
    )


@pytest.fixture
def fake_chart_plot_parameters_headline_data() -> PlotParameters:
    return PlotParameters(
        metric="COVID-19_headline_vaccines_spring24Uptake",
        topic="COVID-19",
        chart_type=ChartTypes.bar,
        x_axis="age",
        y_axis="metric",
        date_from=None,
        date_to=None,
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
def valid_plot_parameters_for_headline_data() -> PlotParameters:
    return PlotParameters(
        metric="COVID-19_headline_vaccines_spring24Uptake",
        topic="COVID-19",
        chart_type=ChartTypes.bar.value,
        date_from="",
        date_to="",
        x_axis="age",
        y_axis="metric",
    )


@pytest.fixture
def fake_plot_data() -> PlotGenerationData:
    plot_params = PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
        x_axis="metric",
        y_axis="date",
        geography="London",
        age="all",
        sex="all",
        line_type="SOLID",
        line_colour="COLOUR_1_DARK_BLUE",
    )
    y_axis_values = [1, 2, 4, 5, 5, 2, 1, 8, 9, 10, 2, 3]
    return PlotGenerationData(
        parameters=plot_params,
        x_axis_values=[
            datetime.date(year=2023, month=i + 1, day=1)
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
                "is_public": True,
            },
            {
                "period_start": "2023-10-23",
                "period_end": "2023-10-30",
                "metric_value": 10.7,
                "embargo": "2023-11-16 17:30:00",
                "is_public": True,
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
                "is_public": True,
            },
            {
                "epiweek": 44,
                "date": "2022-11-02",
                "metric_value": 3952.14,
                "embargo": "2023-11-16 17:30:00",
                "is_public": True,
            },
        ],
    }


@pytest.fixture()
def dashboard_root_page() -> UKHSARootPage:
    root_page = UKHSARootPage(
        title="UKHSA Dashboard Root",
        slug="ukhsa-dashboard-root",
        path="ukhsa-dashboard-root",
        depth=1,
    )
    Locale.objects.get_or_create(language_code="en")

    wagtail_root_page = Page.get_first_root_node() or Page.add_root(
        title="Root", slug="root"
    )
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
        "x_axis_title": "Age",
        "y_axis_title": "Admissions",
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
                    "use_markers": False,
                    "use_smooth_lines": True,
                },
                "id": "791efbf1-8880-4dfa-9f5d-526982ed1539",
            }
        ],
    }


@pytest.fixture
def example_headline_chart_block() -> dict[str, str | list[dict]]:
    return {
        "title": "COVID-19 headline cases 7 Days Total",
        "body": "COVID-19 cases 7 day total by age",
        "x_axis": "age",
        "y_axis": "metric",
        "chart": [
            {
                "type": "plot",
                "value": {
                    "topic": "COVID-19",
                    "metric": "COVID-19_headline_cases_7DayTotals",
                    "chart_type": "bar",
                    "stratum": "",
                    "geography": "England",
                    "geography_type": "Nation",
                    "sex": "",
                    "age": "01-04",
                    "label": "Admission rate",
                    "line_colour": "",
                    "line_type": "",
                    "use_markers": False,
                    "use_smooth_lines": True,
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


@pytest.fixture
def timestamp_2_months_from_now() -> datetime.datetime:
    return datetime.datetime.now() + relativedelta(months=2)
