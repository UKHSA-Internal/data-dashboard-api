import datetime
from decimal import Decimal
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from wagtail.models import Page
from wagtail.models.i18n import Locale

from caching.private_api.management import CacheManagement
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
        "chart_type": ChartTypes.bar.value,
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
                "upper_confidence": 15,
                "metric_value": 12.3,
                "lower_confidence": 10,
                "embargo": "2023-11-16 17:30:00",
                "is_public": True,
            },
            {
                "period_start": "2023-10-23",
                "period_end": "2023-10-30",
                "upper_confidence": 11,
                "metric_value": 10.7,
                "lower_confidence": 8,
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
                "upper_confidence": 4200,
                "metric_value": 4141.43,
                "lower_confidence": 4100.00,
                "embargo": "2023-11-16 17:30:00",
                "is_public": True,
            },
            {
                "epiweek": 44,
                "date": "2022-11-02",
                "upper_confidence": 400.00,
                "metric_value": 3952.14,
                "lower_confidence": 3900.00,
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


@pytest.fixture
def cache_management_with_in_memory_cache() -> CacheManagement:
    return CacheManagement(in_memory=True)


@pytest.fixture
def example_global_filter():
    return {
        "type": "global_filter_card",
        "value": {
            "time_range": {
                "title": "Year selection",
                "time_periods": [
                    {
                        "type": "time_period",
                        "value": {
                            "label": "2023-2024",
                            "date_from": "2023-04-01",
                            "date_to": "2024-03-31",
                        },
                        "id": "cbfb7958-bcb1-4036-881e-0a2fbec79db5",
                    },
                    {
                        "type": "time_period",
                        "value": {
                            "label": "2024-2025",
                            "date_from": "2024-04-01",
                            "date_to": "2025-03-31",
                        },
                        "id": "72ab2c6a-5116-42b9-9f15-25aacd12c467",
                    },
                ],
            },
            "rows": [
                {
                    "type": "row",
                    "value": {
                        "title": "Area",
                        "filters": [
                            {
                                "type": "geography_filters",
                                "value": {
                                    "geography_types": [
                                        {
                                            "type": "geography_filter",
                                            "value": {
                                                "label": "Country",
                                                "colour": "COLOUR_1_DARK_BLUE",
                                                "geography_type": "Nation",
                                            },
                                            "id": "5ed27d55-ffaa-4a8d-8b93-8f20d186265d",
                                        },
                                        {
                                            "type": "geography_filter",
                                            "value": {
                                                "label": "Region",
                                                "colour": "COLOUR_2_TURQUOISE",
                                                "geography_type": "Region",
                                            },
                                            "id": "87c30c92-c9bd-46cd-89eb-6468e46e7b5b",
                                        },
                                        {
                                            "type": "geography_filter",
                                            "value": {
                                                "label": "Local Authority",
                                                "colour": "COLOUR_3_DARK_PINK",
                                                "geography_type": "Upper Tier Local Authority",
                                            },
                                            "id": "b531fee6-149d-429d-8de6-90bf27f4f9e6",
                                        },
                                    ]
                                },
                                "id": "2cb36d1b-6f38-4a92-bc8d-d54fa22fbdf2",
                            }
                        ],
                    },
                    "id": "64c0fc3f-f2db-48a5-b8cf-9ee43c31b11e",
                },
                {
                    "type": "row",
                    "value": {
                        "title": "Vaccination and coverage",
                        "filters": [
                            {
                                "type": "data_filters",
                                "value": {
                                    "label": "Select vaccination",
                                    "data_filters": [
                                        {
                                            "type": "data_filter",
                                            "value": {
                                                "label": "6-in-1 (1 year)",
                                                "colour": "COLOUR_1_DARK_BLUE",
                                                "parameters": {
                                                    "theme": {
                                                        "label": "",
                                                        "value": "immunisation",
                                                    },
                                                    "sub_theme": {
                                                        "label": "",
                                                        "value": "childhood-vaccines",
                                                    },
                                                    "topic": {
                                                        "label": "",
                                                        "value": "6-in-1",
                                                    },
                                                    "stratum": {
                                                        "label": "1 year",
                                                        "value": "12m",
                                                    },
                                                    "metric": {
                                                        "label": "",
                                                        "value": "6-in-1_coverage_coverageByYear",
                                                    },
                                                    "age": {
                                                        "label": "",
                                                        "value": "all",
                                                    },
                                                    "sex": {
                                                        "label": "",
                                                        "value": "all",
                                                    },
                                                },
                                                "accompanying_points": [
                                                    {
                                                        "type": "accompanying_point",
                                                        "value": {
                                                            "label_prefix": "Country level of coverage",
                                                            "label_suffix": "%",
                                                            "parameters": [
                                                                {
                                                                    "type": "geography_type",
                                                                    "value": {
                                                                        "label": "",
                                                                        "value": "Nation",
                                                                    },
                                                                    "id": "7d2d3eaa-e339-44fd-bff5-2dcf0d083d67",
                                                                }
                                                            ],
                                                        },
                                                        "id": "ab8e4f2f-d62b-411c-adff-8a9bb0aa8ac7",
                                                    },
                                                    {
                                                        "type": "accompanying_point",
                                                        "value": {
                                                            "label_prefix": "Region level of coverage",
                                                            "label_suffix": "%",
                                                            "parameters": [
                                                                {
                                                                    "type": "geography_type",
                                                                    "value": {
                                                                        "label": "",
                                                                        "value": "Region",
                                                                    },
                                                                    "id": "d1c05efe-665d-4f19-9ef9-c72eb91187e6",
                                                                }
                                                            ],
                                                        },
                                                        "id": "173d85f8-a865-4d31-b17f-6f95eda1d432",
                                                    },
                                                ],
                                            },
                                            "id": "119e270f-2759-44a0-969a-1651407a109a",
                                        },
                                        {
                                            "type": "data_filter",
                                            "value": {
                                                "label": "MMR1 (1 year)",
                                                "colour": "COLOUR_4_ORANGE",
                                                "parameters": {
                                                    "theme": {
                                                        "label": "",
                                                        "value": "immunisation",
                                                    },
                                                    "sub_theme": {
                                                        "label": "",
                                                        "value": "childhood-vaccines",
                                                    },
                                                    "topic": {
                                                        "label": "",
                                                        "value": "MMR1",
                                                    },
                                                    "stratum": {
                                                        "label": "1 year",
                                                        "value": "12m",
                                                    },
                                                    "metric": {
                                                        "label": "",
                                                        "value": "MMR1_coverage_coverageByYear",
                                                    },
                                                    "age": {
                                                        "label": "",
                                                        "value": "all",
                                                    },
                                                    "sex": {
                                                        "label": "",
                                                        "value": "all",
                                                    },
                                                },
                                                "accompanying_points": [
                                                    {
                                                        "type": "accompanying_point",
                                                        "value": {
                                                            "label_prefix": "Country level of coverage",
                                                            "label_suffix": "%",
                                                            "parameters": [
                                                                {
                                                                    "type": "geography_type",
                                                                    "value": {
                                                                        "label": "",
                                                                        "value": "Nation",
                                                                    },
                                                                    "id": "69ceb950-4880-43f3-b7b0-ee8a1b1b057f",
                                                                }
                                                            ],
                                                        },
                                                        "id": "3b65850e-10f3-48eb-95ed-979c04bcc770",
                                                    },
                                                    {
                                                        "type": "accompanying_point",
                                                        "value": {
                                                            "label_prefix": "Region level of coverage",
                                                            "label_suffix": "%",
                                                            "parameters": [
                                                                {
                                                                    "type": "geography_type",
                                                                    "value": {
                                                                        "label": "",
                                                                        "value": "Region",
                                                                    },
                                                                    "id": "b98498f6-f881-4e1c-8c19-457247200790",
                                                                }
                                                            ],
                                                        },
                                                        "id": "82b5edee-7df8-4ba9-8101-44662331a672",
                                                    },
                                                ],
                                            },
                                            "id": "4645cfe1-e5f7-4bd6-918b-568da9dce48d",
                                        },
                                    ],
                                    "categories_to_group_by": [
                                        {
                                            "type": "category",
                                            "value": {"data_category": "stratum"},
                                            "id": "85acdaf0-540c-49e2-9210-7e6370c574eb",
                                        },
                                        {
                                            "type": "category",
                                            "value": {"data_category": "topic"},
                                            "id": "76fcdb38-db17-4580-8bf0-48bca2881b4a",
                                        },
                                    ],
                                },
                                "id": "8c0e75e3-4399-45f8-b9f2-944ce631960e",
                            },
                            {
                                "type": "threshold_filters",
                                "value": {
                                    "label": "Select level of coverage (%)",
                                    "thresholds": [
                                        {
                                            "type": "threshold",
                                            "value": {
                                                "label": "Under 80%",
                                                "colour": "COLOUR_1_DARK_BLUE",
                                                "boundary_minimum_value": "0",
                                                "boundary_maximum_value": "0.8",
                                            },
                                            "id": "9019a648-901c-4801-9d3e-d3b95242a58e",
                                        },
                                        {
                                            "type": "threshold",
                                            "value": {
                                                "label": "80-85%",
                                                "colour": "COLOUR_2_TURQUOISE",
                                                "boundary_minimum_value": "0.81",
                                                "boundary_maximum_value": "0.85",
                                            },
                                            "id": "9137b412-ef3a-4d39-8662-1096ba1c3b99",
                                        },
                                        {
                                            "type": "threshold",
                                            "value": {
                                                "label": "85-90%",
                                                "colour": "COLOUR_3_DARK_PINK",
                                                "boundary_minimum_value": "0.86",
                                                "boundary_maximum_value": "0.9",
                                            },
                                            "id": "38cd3f76-46ed-41d9-a7a2-9a41510c0b2d",
                                        },
                                        {
                                            "type": "threshold",
                                            "value": {
                                                "label": "90-95%",
                                                "colour": "COLOUR_4_ORANGE",
                                                "boundary_minimum_value": "0.91",
                                                "boundary_maximum_value": "0.95",
                                            },
                                            "id": "3584882d-ce37-4d57-abcb-ac0d71133dc5",
                                        },
                                        {
                                            "type": "threshold",
                                            "value": {
                                                "label": "Over 95%",
                                                "colour": "COLOUR_5_DARK_GREY",
                                                "boundary_minimum_value": "0.96",
                                                "boundary_maximum_value": "1.00",
                                            },
                                            "id": "d8583ba3-259f-49f0-be86-eaa670198c25",
                                        },
                                    ],
                                },
                                "id": "b029909f-588d-4a13-90db-7e08e7e20f3d",
                            },
                        ],
                    },
                    "id": "854569f8-0cd0-4fbf-bf21-b8eadeb613cb",
                },
            ],
        },
        "id": "da1c5477-4e98-4686-8fa2-2af05d50a701",
    }
