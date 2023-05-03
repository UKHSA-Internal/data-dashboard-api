import pytest

from metrics.domain.models import ChartPlotParameters


@pytest.fixture
def fake_chart_plot_parameters() -> ChartPlotParameters:
    return ChartPlotParameters(
        chart_type="line_multi_coloured",
        topic="RSV",
        metric="weekly_positivity_by_age",
        stratum="0_4",
    )
