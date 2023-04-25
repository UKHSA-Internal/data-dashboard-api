import datetime
from typing import List

import plotly.graph_objects

from metrics.domain.charts.bar.colour_scheme import RGBAColours
from metrics.domain.charts.bar.generation import generate_chart_figure

DATES: List[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2023, 1, 9),
]
VALUES: List[int] = [1, 2, 3, 4, 5, 6]


class TestBarCharts:
    def test_main_layout(self):
        """
        Given a list of dates and values for data points
        When `generate_chart_figure()` is called from the `bar` module
        Then the figure is drawn with the expected parameters
        """
        # Given
        dates = DATES
        values = VALUES

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            dates=dates,
            values=values,
            legend="Plot 1",
        )

        # Then
        main_layout: plotly.graph_objects.Layout = figure.layout

        # Check that the main background colour is a plain white and legend is being shown
        assert main_layout.plot_bgcolor == RGBAColours.WHITE.stringified
        assert main_layout.paper_bgcolor == RGBAColours.WHITE.stringified
        assert main_layout.showlegend

    def test_main_bar_plot(self):
        """
        Given a list of dates & values
        When `generate_chart_figure()` is called from the `bar` module
        Then the figure is drawn with the expected parameters for the main plot
        """
        # Given
        dates = DATES
        values = VALUES
        legend = "Plot 1"

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            dates=dates,
            values=values,
            legend=legend,
        )

        # Then
        assert len(figure.data) == 1

        # ---Main line plot checks---
        main_bar_plot: plotly.graph_objects.Bar = figure.data[0]

        # Check it is a Bar chart
        assert type(main_bar_plot) == plotly.graph_objects.Bar

        # Check x & y values were correctly assigned
        assert main_bar_plot.x == tuple(dates)
        assert main_bar_plot.y == tuple(values)

        # Bars should be Blue
        assert main_bar_plot.marker.color == RGBAColours.PLOT_1_BLUE.stringified

        # Legend is assigned
        assert main_bar_plot.name == legend
