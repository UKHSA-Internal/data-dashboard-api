import datetime
from typing import List
from unittest import mock

import plotly

from metrics.domain.charts.line_multi_coloured import generation
from metrics.domain.models import PlotParameters, PlotData
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts.access import ChartsInterface


class TestChartsInterface:
    @staticmethod
    def _create_chart_plot_data(
        x_axis_values: List[datetime.date],
        y_axis_values: List[int],
    ) -> PlotData:
        plot_params = PlotParameters(
            chart_type="line_multi_coloured",
            topic="RSV",
            metric="weekly_positivity_by_age",
        )
        return PlotData(
            parameters=plot_params,
            x_axis_values=x_axis_values,
            y_axis_values=y_axis_values,
        )

    @staticmethod
    def _create_charts_interface() -> ChartsInterface:
        chart_type: str = ChartTypes.line_multi_coloured.value
        mocked_chart_plot_params = mock.Mock(chart_type=chart_type)
        mocked_chart_plots = mock.Mock(plots=[mocked_chart_plot_params])

        return ChartsInterface(
            chart_plots=mocked_chart_plots,
            core_time_series_manager=mock.Mock(),
        )

    plot_1_dates: List[datetime.date] = [
        datetime.date(2022, 9, 5),
        datetime.date(2022, 9, 19),
        datetime.date(2022, 10, 3),
        datetime.date(2022, 10, 7),
        datetime.date(2022, 10, 21),
        datetime.date(2022, 11, 3),
        datetime.date(2022, 11, 14),
        datetime.date(2022, 12, 12),
        datetime.date(2022, 12, 26),
        datetime.date(2023, 1, 9),
    ]
    plot_1_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    plot_2_dates: List[datetime.date] = [
        datetime.date(2020, 9, 5),
        datetime.date(2022, 9, 19),
        datetime.date(2023, 3, 9),
    ]
    plot_2_values = [10, 20, 30]

    first_chart_plots_data = _create_chart_plot_data(
        x_axis_values=plot_1_dates,
        y_axis_values=plot_1_values,
    )

    second_chart_plots_data = _create_chart_plot_data(
        x_axis_values=plot_2_dates,
        y_axis_values=plot_2_values,
    )

    mock_charts_interface = _create_charts_interface()

    def test_determine_get_last_updated_where_chart_has_dates(self):
        """
        Given a multi coloured line chart with two plots
        and with dates along the x-axis
        When `get_last_updated()` is called
        Then we get back the latest date in the chart
        """

        # Given
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            chart_height=200,
            chart_width=200,
            chart_plots_data=[
                self.first_chart_plots_data,
                self.second_chart_plots_data,
            ],
        )

        # When
        last_updated_date: str = self.mock_charts_interface.get_last_updated(figure)

        # Then
        expected_date: str = "2023-03-09"

        assert last_updated_date == expected_date

    def test_determine_last_updated_where_chart_does_not_have_dates(self):
        """
        Given a multi coloured line chart with two plots
        and with something other than dates along the x axis
        When `get_last_updated()` is called
        Then we get back nothing
        """

        # Given
        figure: plotly.graph_objects.Figure = generation.generate_chart_figure(
            chart_height=200,
            chart_width=200,
            chart_plots_data=[
                self.first_chart_plots_data,
                self.second_chart_plots_data,
            ],
        )

        # Simulate the chart has something other than dates along the x axis
        figure.update_xaxes({"type": "-"})

        # When
        last_updated_date: str = self.mock_charts_interface.get_last_updated(figure)

        # Then
        expected_date: str = ""

        assert last_updated_date == expected_date
