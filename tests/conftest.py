import pytest

from metrics.domain.models import ChartPlotParameters, TablePlotParameters


@pytest.fixture
def fake_chart_plot_parameters() -> ChartPlotParameters:
    return ChartPlotParameters(
        chart_type="line_multi_coloured",
        topic="RSV",
        metric="weekly_positivity_by_age",
        stratum="0_4",
    )


@pytest.fixture
def fake_table_plot_parameters() -> ChartPlotParameters:
    return TablePlotParameters(
        topic="RSV",
        metric="weekly_positivity_by_age",
        stratum="0_4",
    )


@pytest.fixture
def fake_chart_plot_parameters_covid_cases() -> ChartPlotParameters:
    return ChartPlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="new_cases_daily",
    )


@pytest.fixture
def fake_table_plot_parameters_covid_cases() -> TablePlotParameters:
    return TablePlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="new_cases_daily",
    )
