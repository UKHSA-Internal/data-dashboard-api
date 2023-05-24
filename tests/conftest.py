import pytest

from metrics.domain.models import PlotParameters


@pytest.fixture
def fake_chart_plot_parameters() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="RSV",
        metric="weekly_positivity_by_age",
        stratum="0_4",
        date_from="2023-01-01",
    )


@pytest.fixture
def fake_chart_plot_parameters_covid_cases() -> PlotParameters:
    return PlotParameters(
        chart_type="line_multi_coloured",
        topic="COVID-19",
        metric="new_cases_daily",
    )
