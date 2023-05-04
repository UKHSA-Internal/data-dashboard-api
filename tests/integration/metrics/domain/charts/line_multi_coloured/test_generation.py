import datetime
from typing import List

import plotly.graph_objects

from metrics.domain.charts.line_with_shaded_section import colour_scheme, generation
from metrics.domain.models import ChartPlotData, ChartPlotParameters

DATES_FROM_SEP_TO_JAN: List[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2023, 1, 9),
]


class TestLineMultiColouredCharts:
    def test_two_plots_with_provided_labels(self, fake_chart_plot_parameters: ChartPlotParameters):
        """
        Given
        When
        Then
        """
        # Given
        chart_plots_data = ChartPlotData()
        dates = DATES_FROM_SEP_TO_JAN
        values = [10, 22, 8, 65, 92]
        chart_plots_data.data = dates, values

        # When


        # Then
