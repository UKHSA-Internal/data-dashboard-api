import datetime
from unittest import mock

import plotly.graph_objects
import pytest

from metrics.domain.charts.common_charts.generation import generate_chart_figure
from metrics.domain.charts.colour_scheme import RGBAChartLineColours, RGBAColours
from metrics.domain.models.plots import (
    ChartGenerationPayload,
    PlotGenerationData,
)

HEIGHT = 300
WIDTH = 400


@pytest.fixture
def mocked_plot_data() -> mock.Mock:
    dates = [
        datetime.date(2022, 9, 5),
        datetime.date(2022, 10, 10),
        datetime.date(2022, 11, 14),
        datetime.date(2022, 12, 12),
        datetime.date(2023, 1, 9),
    ]
    values = [i + 1 for i in range(len(dates))]

    parameters = mock.Mock(label="Plot1")
    return mock.Mock(
        x_axis_values=dates,
        y_axis_values=values,
        parameters=parameters,
    )


class TestBarCharts:
    def test_main_layout(self, fake_plot_data: PlotGenerationData):
        """
        Given a list of dates and values for data points
        When `generate_chart_figure()` is called from the `bar` module
        Then the figure is drawn with the expected parameters
        """
        # Given
        chart_plots_data = [fake_plot_data]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        main_layout: plotly.graph_objects.Layout = figure.layout

        # Check that the main background colour is a plain white and legend is being shown
        assert main_layout.plot_bgcolor == RGBAColours.WHITE.stringified
        assert main_layout.paper_bgcolor == RGBAColours.WHITE.stringified

        # Check the chart sizes are as per the specified parameters
        assert main_layout.height == HEIGHT
        assert main_layout.width == WIDTH

        # Check left and right margins are both 0
        assert main_layout.margin.l == main_layout.margin.r == 0

    def test_main_bar_plot(self, fake_plot_data: PlotGenerationData):
        """
        Given a list of dates & values
        When `generate_chart_figure()` is called from the `bar` module
        Then the figure is drawn with the expected parameters for the main plot
        """
        # Given
        chart_plots_data = [fake_plot_data]
        chart_plots_data[0].parameters.chart_type = "bar"
        fake_plot_data.additional_values = {
            "in_reporting_delay_period": [True] * len(fake_plot_data.x_axis_values)
        }
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        # There should be 1 plot for the bar plot
        # and another dummy plot for the reporting delay period
        assert len(figure.data) == 2

        # ---Main bar plot checks---
        main_bar_plot: plotly.graph_objects.Bar = figure.data[0]

        # Check it is a Bar chart
        assert type(main_bar_plot) == plotly.graph_objects.Bar

        # Check x & y values were correctly assigned
        # Note that the dates along the x-axis are returned as strings
        # i.e. `2022-9-5` instead of as datetime objects hence the need for the string conversion
        assert main_bar_plot.x == tuple([str(x) for x in fake_plot_data.x_axis_values])
        assert main_bar_plot.y == tuple(fake_plot_data.y_axis_values)

        # Bars should be Blue
        assert (
            main_bar_plot.marker.color
            == RGBAChartLineColours.COLOUR_1_DARK_BLUE.stringified
        )
        assert (
            main_bar_plot.marker.line.color
            == RGBAChartLineColours.COLOUR_1_DARK_BLUE.stringified
        )
        assert main_bar_plot.marker.line.width == 1

        # Legend is assigned
        assert main_bar_plot.name == fake_plot_data.parameters.label

        # ---X Axis checks---
        x_axis = figure.layout.xaxis

        assert x_axis.showgrid
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
        # The chart width is narrow, so the tick labels will use a newline to break the month and year text
        assert x_axis.tickformat == "%b<br>%Y"

        # ---Y Axis checks---
        y_axis = figure.layout.yaxis
        assert not y_axis.showgrid
        assert y_axis.showticklabels

    def test_confidence_intervals_all_data(self, fake_plot_data: PlotGenerationData):
        """
        Given a list of dates & values
        And the confidence_intervals parameter is true
        And the data has both upper_confidence and lower_confidence values
        When `generate_chart_figure()` is called from the `bar` module
        Then it has error bars
        """
        # Given
        chart_plots_data = [fake_plot_data]
        chart_plots_data[0].parameters.chart_type = "bar"
        fake_plot_data.additional_values = {
            "upper_confidence": [2] * len(fake_plot_data.x_axis_values),
            "lower_confidence": [1] * len(fake_plot_data.x_axis_values),
        }
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
            confidence_intervals=True,
            confidence_colour="BLUE",
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        # There should be 1 plot for the bar plot
        assert len(figure.data) == 1

        # ---Main bar plot checks---
        main_bar_plot: plotly.graph_objects.Bar = figure.data[0]

        # Check it is a Bar chart
        assert type(main_bar_plot) == plotly.graph_objects.Bar
        # Check there are error bars
        assert main_bar_plot.error_y != None

    def test_confidence_intervals_missing_data_no_lower(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of dates & values
        And the confidence_intervals parameter is true
        And the data is missing either upper_confidence or lower_confidence values
        When `generate_chart_figure()` is called from the `bar` module
        Then it does not draw confidence intervals
        """
        # Given
        chart_plots_data = [fake_plot_data]
        chart_plots_data[0].parameters.chart_type = "bar"
        fake_plot_data.additional_values = {
            "upper_confidence": [2] * len(fake_plot_data.x_axis_values),
        }
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
            confidence_intervals=True,
            confidence_colour="BLUE",
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        # There should be 1 plot for the bar plot
        assert len(figure.data) == 1

        main_bar_plot: plotly.graph_objects.Bar = figure.data[0]
        # There should not be a populated error object
        assert main_bar_plot.error_y.array is None
        assert main_bar_plot.error_y.arrayminus is None

    def test_confidence_intervals_missing_data_no_upper(
        self, fake_plot_data: PlotGenerationData
    ):
        # Given
        chart_plots_data = [fake_plot_data]
        chart_plots_data[0].parameters.chart_type = "bar"
        fake_plot_data.additional_values = {
            "lower_confidence": [2] * len(fake_plot_data.x_axis_values),
        }
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
            confidence_intervals=True,
            confidence_colour="BLUE",
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        # There should be 1 plot for the bar plot
        assert len(figure.data) == 1

        main_bar_plot: plotly.graph_objects.Bar = figure.data[0]
        # There should not be a populated error object
        assert main_bar_plot.error_y.array is None
        assert main_bar_plot.error_y.arrayminus is None

    def test_confidence_intervals_missing_data_nones_in_values(
        self, fake_plot_data: PlotGenerationData
    ):
        # Given
        chart_plots_data = [fake_plot_data]
        chart_plots_data[0].parameters.chart_type = "bar"
        # Check that it works if there's a mix of None and Values
        fake_plot_data.additional_values = {
            "lower_confidence": [None]
            + ([1] * (len(fake_plot_data.x_axis_values) - 1)),
            "upper_confidence": [2] * len(fake_plot_data.x_axis_values),
        }
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
            confidence_intervals=True,
            confidence_colour="BLUE",
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        # There should be 1 plot for the bar plot
        assert len(figure.data) == 1

        main_bar_plot: plotly.graph_objects.Bar = figure.data[0]
        # There should not be a populated error object
        assert main_bar_plot.error_y.array is not None
        assert main_bar_plot.error_y.arrayminus is not None

    def test_x_axis_type_is_not_date(self, fake_plot_data: PlotGenerationData):
        """
        Given a list of x and y values where x values are NOT dates
        When `generate_chart_figure()` is called from the `bar` module
        Then the figure is drawn with the expected parameters for the x axis
        """
        # Given
        x_axis_values = ["0-4", "5-8", "9-29"]
        fake_plot_data.x_axis_values = x_axis_values
        chart_plots_data = [fake_plot_data]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=chart_plots_data,
            x_axis_title="",
            y_axis_title="",
            y_axis_minimum_value=0,
            y_axis_maximum_value=None,
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=chart_payload
        )

        # Then
        # Check left and right margins are both 0
        assert figure.layout.margin.l == 0
        assert figure.layout.margin.r == 0

        # ---X Axis checks---
        x_axis = figure.layout.xaxis

        # The `M1` dtick setting is only valid for dates
        assert x_axis.dtick is None

        # The x-axis type and ticks should be the default
        assert x_axis.type == "-"
        assert x_axis.tickformat is None
