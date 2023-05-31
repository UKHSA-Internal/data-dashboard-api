import datetime
from typing import List

import plotly.graph_objects

from metrics.domain.charts.bar.generation import generate_chart_figure
from metrics.domain.charts.colour_scheme import RGBAColours

DATES: List[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2023, 1, 9),
]
VALUES: List[int] = [1, 2, 3, 4, 5, 6]
HEIGHT = 300
WIDTH = 400


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
            chart_height=HEIGHT,
            chart_width=WIDTH,
            dates=dates,
            values=values,
            legend="Plot 1",
        )

        # Then
        main_layout: plotly.graph_objects.Layout = figure.layout

        # Check that the main background colour is a plain white and legend is being shown
        assert main_layout.plot_bgcolor == RGBAColours.WHITE.stringified
        assert main_layout.paper_bgcolor == RGBAColours.WHITE.stringified

        # Check the chart sizes are as per the specified parameters
        assert main_layout.height == HEIGHT
        assert main_layout.width == WIDTH

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
            chart_height=HEIGHT,
            chart_width=WIDTH,
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
        assert main_bar_plot.marker.color == RGBAColours.BAR_PLOT_1_BLUE.stringified
        assert (
            main_bar_plot.marker.line.color == RGBAColours.BAR_PLOT_1_BLUE.stringified
        )
        assert main_bar_plot.marker.line.width == 1

        # Legend is assigned
        assert main_bar_plot.name == legend

        # ---X Axis checks---
        x_axis = figure.layout.xaxis

        assert not x_axis.showgrid
        assert not x_axis.zeroline
        assert not x_axis.showline

        # Tick marks should be on the boundary drawn going outwards of the main frame
        assert x_axis.ticks == "outside"
        assert x_axis.tickson == "boundaries"

        # The `M1` dtick setting ensures x values within the same month do not show repeated months:
        # ___Sep___Oct___Nov___  as opposed to _Sep_Sep_Oct_Oct_Oct_Nov_Nov_
        assert x_axis.dtick == "M1"

        # The x-axis ticks should be formatted as shorthand Months only i.e Sep not September
        assert x_axis.type == "date"
        assert x_axis.tickformat == "%b %Y"

        # ---Y Axis checks---
        y_axis = figure.layout.yaxis
        assert not y_axis.showgrid
        assert y_axis.showticklabels
