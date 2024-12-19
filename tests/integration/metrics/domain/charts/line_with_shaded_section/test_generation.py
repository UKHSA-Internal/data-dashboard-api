import datetime
from unittest import mock

import plotly.graph_objects

from metrics.domain.charts.colour_scheme import RGBAColours
from metrics.domain.charts.line_with_shaded_section import generation
from metrics.domain.models import PlotGenerationData

DATES_FROM_SEP_TO_JAN: list[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2023, 1, 9),
]
METRIC_NAME: str = "COVID-19_deaths_ONSByWeek"
HEIGHT = 220
WIDTH = 930


class TestLineWithShadedSectionCharts:
    def test_weekly_hospital_admissions_rate_main_plot(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of dates and values
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the main background and the X & Y axis
        """
        # Given
        x_axis_values = DATES_FROM_SEP_TO_JAN
        y_axis_values = [1.1, 0.9, 0.8, 0.6, 0.3]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            plots_data=[fake_plot_data],
            chart_height=HEIGHT,
            chart_width=WIDTH,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            rolling_period_slice=1,
            metric_name=METRIC_NAME,
            change_in_metric_value=-0.3,
        )

        # Then
        # ---Main background checks---
        main_layout = figure.layout
        # Check that the main background colour is a plain white
        assert main_layout.paper_bgcolor == RGBAColours.WHITE.stringified
        assert not main_layout.showlegend

        # Check left and right margins are both 0
        assert figure.layout.margin.l == figure.layout.margin.r == 0

        # Check the chart sizes are as per the specified parameters
        assert main_layout.height == HEIGHT
        assert main_layout.width == WIDTH

        # ---X Axis checks---
        x_axis = main_layout.xaxis
        # The `M1` dtick setting ensures x values within the same month do not show repeated months:
        # ___Sep___Oct___Nov___  as opposed to _Sep_Sep_Oct_Oct_Oct_Nov_Nov_
        assert x_axis.dtick == "M1"

        assert x_axis.showgrid

        # Tick marks should be on the boundary drawn going outwards of the main frame
        assert x_axis.ticks == "outside"
        assert x_axis.tickson == "boundaries"

        # The x-axis ticks should be formatted as shorthand Months only i.e Sep not September
        assert x_axis.type == "date"
        assert x_axis.tickformat == "%b %Y"

        # ---Y Axis checks---
        y_axis = main_layout.yaxis
        assert not y_axis.showgrid
        assert y_axis.showticklabels

    def test_x_axis_type_is_not_date(self):
        """
        Given a list of x and y values where x values are NOT dates
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the x axis
        """
        # Given
        x_axis_values = ["0-4", "5-8", "9-29"]
        y_axis_values = [1.1, 0.9, 0.8, 0.6, 0.3]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            plots_data=mock.MagicMock(),  # Stubbed
            chart_height=HEIGHT,
            chart_width=WIDTH,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            rolling_period_slice=1,
            metric_name=METRIC_NAME,
            change_in_metric_value=-0.3,
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

    def test_weekly_hospital_admissions_rate_increasing_plot(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of dates and values indicating an increase in `COVID-19_deaths_ONSByWeek`
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the main line and the shaded section plot
        """
        # Given
        x_axis_values = DATES_FROM_SEP_TO_JAN
        x_axis_values_as_strings = [str(x) for x in x_axis_values]
        y_axis_values = [0.3, 0.3, 0.4, 0.6, 0.8]
        metric_name = METRIC_NAME
        rolling_period_slice = 1
        increasing_metric_value = 0.2

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            plots_data=[fake_plot_data],
            chart_height=HEIGHT,
            chart_width=WIDTH,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            rolling_period_slice=rolling_period_slice,
            metric_name=metric_name,
            change_in_metric_value=increasing_metric_value,
        )

        # Then
        assert len(figure.data) == 2

        # ---Main line plot checks---
        # There should only be 2 plots on the figure, one for the main line and another for the highlighted region
        main_line_plot: plotly.graph_objects.Scatter = figure.data[0]

        # The main line should be drawn as a neutral dark grey `spline` plot
        main_line = main_line_plot.line
        assert main_line.color == RGBAColours.LS_DARK_GREY.stringified
        assert main_line.shape == "spline"

        # The main line should also not include the last number of points denoted by the `rolling_period_slice` arg
        index_slice_excluding_rolling_period_slice = -rolling_period_slice
        assert list(main_line_plot.x) == list(
            x_axis_values_as_strings[:index_slice_excluding_rolling_period_slice]
        )
        # Note that the dates along the x-axis are returned as strings
        # i.e. `2022-9-5` instead of as datetime objects hence the need for the string conversion
        assert list(main_line_plot.y) == list(
            y_axis_values[:index_slice_excluding_rolling_period_slice]
        )

        # ---Shaded section plot checks---
        shaded_section_plot: plotly.graph_objects.Scatter = figure.data[1]
        # The shaded section plot should be drawn as a spline plot with a line colour of dark red
        assert shaded_section_plot.line.color == RGBAColours.DARK_RED.stringified
        assert shaded_section_plot.line.shape == "spline"

        # The shaded section plot should be filled with a light red colour of 50% opacity
        assert shaded_section_plot.fillcolor == RGBAColours.LIGHT_RED.stringified
        assert shaded_section_plot.opacity == 0.5

        # The shaded section plot should only include the last number of points
        # denoted by the `rolling_period_slice` arg
        index_slice_including_only_rolling_period = -(rolling_period_slice + 1)
        assert list(shaded_section_plot.x) == list(
            x_axis_values_as_strings[index_slice_including_only_rolling_period:]
        )
        assert list(shaded_section_plot.y) == list(
            y_axis_values[index_slice_including_only_rolling_period:]
        )

    def test_weekly_hospital_admissions_rate_decreasing_plot(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given a list of dates and values indicating a decrease in `COVID-19_deaths_ONSByWeek`
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the main line and the highlighted region plot
        """
        # Given
        x_axis_values = DATES_FROM_SEP_TO_JAN
        x_axis_values_as_strings = [str(x) for x in x_axis_values]
        y_axis_values = [1.1, 0.9, 0.8, 0.6, 0.3]
        metric_name = METRIC_NAME
        rolling_period_slice = 1
        decreasing_metric_value = -0.3

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            plots_data=[fake_plot_data],
            chart_height=HEIGHT,
            chart_width=WIDTH,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
            rolling_period_slice=rolling_period_slice,
            metric_name=metric_name,
            change_in_metric_value=decreasing_metric_value,
        )

        # Then
        assert len(figure.data) == 2

        # ---Main line plot checks---
        # There should only be 2 plots on the figure, one for the main line and another for the highlighted region
        main_line_plot: plotly.graph_objects.Scatter = figure.data[0]

        # The main line should be drawn as a neutral dark grey `spline` plot
        main_line = main_line_plot.line
        assert main_line.color == RGBAColours.LS_DARK_GREY.stringified
        assert main_line.shape == "spline"

        # The main line should also not include the last number of points denoted by the `rolling_period_slice` arg
        index_slice_excluding_rolling_period_slice = -rolling_period_slice
        assert list(main_line_plot.x) == list(
            x_axis_values_as_strings[:index_slice_excluding_rolling_period_slice]
        )
        # Note that the dates along the x-axis are returned as strings
        # i.e. `2022-9-5` instead of as datetime objects hence the need for the string conversion
        assert list(main_line_plot.y) == list(
            y_axis_values[:index_slice_excluding_rolling_period_slice]
        )

        # ---Shaded section plot checks---
        shaded_section_plot: plotly.graph_objects.Scatter = figure.data[1]
        # The shaded section plot should be drawn as a spline plot with a line colour of dark green
        assert shaded_section_plot.line.color == RGBAColours.LS_DARK_GREEN.stringified
        assert shaded_section_plot.line.shape == "spline"

        # The shaded section plot should be filled with a light green colour of 50% opacity
        assert shaded_section_plot.fillcolor == RGBAColours.LS_LIGHT_GREEN.stringified
        assert shaded_section_plot.opacity == 0.5

        # The shaded section plot should only include the last number of points
        # denoted by the `rolling_period_slice` arg
        index_slice_including_only_rolling_period = -(rolling_period_slice + 1)
        assert list(shaded_section_plot.x) == list(
            x_axis_values_as_strings[index_slice_including_only_rolling_period:]
        )
        assert list(shaded_section_plot.y) == list(
            y_axis_values[index_slice_including_only_rolling_period:]
        )
