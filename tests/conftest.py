import pytest

from metrics.domain.models import PlotParameters
from metrics.domain.utils import ChartTypes


@pytest.fixture
def fake_chart_plot_parameters() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="RSV",
        metric="weekly_positivity_by_age",
        stratum="0_4",
        date_from="2023-01-01",
        x_axis="dt",
        y_axis="metric_value",
    )


@pytest.fixture
def fake_chart_plot_parameters_covid_cases() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="new_cases_daily",
    )


@pytest.fixture
def valid_plot_parameters() -> PlotParameters:
    return PlotParameters(
        metric="new_cases_daily",
        topic="COVID-19",
        chart_type=ChartTypes.simple_line.value,
        date_from="2022-01-01",
        x_axis="dt",
        y_axis="metric_value",
    )
