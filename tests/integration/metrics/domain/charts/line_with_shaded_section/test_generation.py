import datetime
from typing import List

import plotly.graph_objects

from metrics.domain.charts.line_with_shaded_section import colour_scheme, generation

DATES_FROM_SEP_TO_JAN: List[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 10, 10),
    datetime.date(2022, 11, 14),
    datetime.date(2022, 12, 12),
    datetime.date(2023, 1, 9),
]
WEEKLY_HOSPITAL_ADMISSIONS_RATE_METRIC: str = "weekly_hospital_admissions_rate"


class TestLineWithShadedSectionCharts:
    def test_weekly_hospital_admissions_rate_main_plot(self):
        """
        Given a list of dates and values
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the main background and the X & Y axis
        """
        # Given
        dates = DATES_FROM_SEP_TO_JAN
        values = [1.1, 0.9, 0.8, 0.6, 0.3]

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            dates=dates,
            values=values,
            rolling_period_slice=1,
            metric_name=WEEKLY_HOSPITAL_ADMISSIONS_RATE_METRIC,
            change_in_metric_value=-0.3,
        )

        # Then
        # ---Main background checks---
        main_layout = figure.layout
        # Check that the main background colour is a plain white
        assert main_layout.paper_bgcolor == colour_scheme.RGBAColours.WHITE.stringified
        assert not main_layout.showlegend

        # ---X Axis checks---
        x_axis = main_layout.xaxis
        # The `M1` dtick setting ensures x values within the same month do not show repeated months:
        # ___Sep___Oct___Nov___  as opposed to _Sep_Sep_Oct_Oct_Oct_Nov_Nov_
        assert x_axis.dtick == "M1"

        assert not x_axis.showgrid

        # Tick marks should be on the boundary drawn going outwards of the main frame
        assert x_axis.ticks == "outside"
        assert x_axis.tickson == "boundaries"

        # The x-axis ticks should be formatted as shorthand Months only i.e Sep not September
        assert x_axis.type == "date"
        assert x_axis.tickformat == "%b %Y"

        # ---Y Axis checks---
        y_axis = main_layout.yaxis
        assert not y_axis.showgrid
        assert not y_axis.showticklabels

    def test_weekly_hospital_admissions_rate_increasing_plot(self):
        """
        Given a list of dates and values indicating an increase in `weekly_hospital_admissions_rate`
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the main line and the shaded section plot
        """
        # Given
        dates = DATES_FROM_SEP_TO_JAN
        values = [0.3, 0.3, 0.4, 0.6, 0.8]
        metric_name = WEEKLY_HOSPITAL_ADMISSIONS_RATE_METRIC
        rolling_period_slice = 1
        increasing_metric_value = 0.2

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            dates=dates,
            values=values,
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
        assert main_line.color == colour_scheme.RGBAColours.DARK_GREY.stringified
        assert main_line.shape == "spline"

        # The main line should also not include the last number of points denoted by the `rolling_period_slice` arg
        index_slice_excluding_rolling_period_slice = -rolling_period_slice
        assert list(main_line_plot.x) == list(
            dates[:index_slice_excluding_rolling_period_slice]
        )
        assert list(main_line_plot.y) == list(
            values[:index_slice_excluding_rolling_period_slice]
        )

        # ---Shaded section plot checks---
        shaded_section_plot: plotly.graph_objects.Scatter = figure.data[1]
        # The shaded section plot should be drawn as a spline plot with a line colour of dark red
        assert (
            shaded_section_plot.line.color
            == colour_scheme.RGBAColours.DARK_RED.stringified
        )
        assert shaded_section_plot.line.shape == "spline"

        # The shaded section plot should be filled with a light red colour of 50% opacity
        assert (
            shaded_section_plot.fillcolor
            == colour_scheme.RGBAColours.LIGHT_RED.stringified
        )
        assert shaded_section_plot.opacity == 0.5

        # The shaded section plot should only include the last number of points
        # denoted by the `rolling_period_slice` arg
        index_slice_including_only_rolling_period = -(rolling_period_slice + 1)
        assert list(shaded_section_plot.x) == list(
            dates[index_slice_including_only_rolling_period:]
        )
        assert list(shaded_section_plot.y) == list(
            values[index_slice_including_only_rolling_period:]
        )

    def test_weekly_hospital_admissions_rate_decreasing_plot(self):
        """
        Given a list of dates and values indicating a decrease in `weekly_hospital_admissions_rate`
        When `generate_chart_figure()` is called from the `line_with_shaded_section` module
        Then the figure is drawn with the expected parameters for the main line and the highlighted region plot
        """
        # Given
        dates = DATES_FROM_SEP_TO_JAN
        values = [1.1, 0.9, 0.8, 0.6, 0.3]
        metric_name = WEEKLY_HOSPITAL_ADMISSIONS_RATE_METRIC
        rolling_period_slice = 1
        decreasing_metric_value = -0.3

        # When
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            dates=dates,
            values=values,
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
        assert main_line.color == colour_scheme.RGBAColours.DARK_GREY.stringified
        assert main_line.shape == "spline"

        # The main line should also not include the last number of points denoted by the `rolling_period_slice` arg
        index_slice_excluding_rolling_period_slice = -rolling_period_slice
        assert list(main_line_plot.x) == list(
            dates[:index_slice_excluding_rolling_period_slice]
        )
        assert list(main_line_plot.y) == list(
            values[:index_slice_excluding_rolling_period_slice]
        )

        # ---Shaded section plot checks---
        shaded_section_plot: plotly.graph_objects.Scatter = figure.data[1]
        # The shaded section plot should be drawn as a spline plot with a line colour of dark green
        assert (
            shaded_section_plot.line.color
            == colour_scheme.RGBAColours.DARK_GREEN.stringified
        )
        assert shaded_section_plot.line.shape == "spline"

        # The shaded section plot should be filled with a light green colour of 50% opacity
        assert (
            shaded_section_plot.fillcolor
            == colour_scheme.RGBAColours.LIGHT_GREEN.stringified
        )
        assert shaded_section_plot.opacity == 0.5

        # The shaded section plot should only include the last number of points
        # denoted by the `rolling_period_slice` arg
        index_slice_including_only_rolling_period = -(rolling_period_slice + 1)
        assert list(shaded_section_plot.x) == list(
            dates[index_slice_including_only_rolling_period:]
        )
        assert list(shaded_section_plot.y) == list(
            values[index_slice_including_only_rolling_period:]
        )
