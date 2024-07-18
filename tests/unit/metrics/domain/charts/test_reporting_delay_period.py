from unittest import mock

import pytest
from plotly.graph_objs import Scatter

from metrics.domain.charts import reporting_delay_period
from metrics.domain.models import PlotData

MODULE_PATH = "metrics.domain.charts.reporting_delay_period"


class TestGetXValueAtStartOfReportingDelayPeriod:
    def test_returns_correct_value(self, fake_plot_data: PlotData):
        """
        Given an enriched `PlotData` model
            which holds a list of reporting delay period booleans
        When `_get_x_value_at_start_of_reporting_delay_period()` is called
        Then the corresponding x value denoted
            by the first occurring True value
            in the reporting delay period is returned
        """
        # Given
        x_axis_value = [0, 1, 2, 3, 4, 5]
        reporting_delay_period_values = [False, False, False, False, True, True]
        fake_plot_data.additional_values = {
            "in_reporting_delay_period": reporting_delay_period_values
        }
        fake_plot_data.x_axis_values = x_axis_value

        # When
        x_value = (
            reporting_delay_period._get_x_value_at_start_of_reporting_delay_period(
                chart_plots_data=[fake_plot_data]
            )
        )

        # Then
        assert x_value == x_axis_value[4]


class TestGetLastXValueAtEndOfReportingDelayPeriod:
    def test_returns_last_x_value_in_plots(self):
        """
        Given a figure which contains plots with various dates
        When `_get_last_x_value_at_end_of_reporting_delay_period()` is called
        Then the latest associated date value is returned
        """
        # Given
        latest_date = "2024-06-09"
        data = [
            {"x": ["2023-01-01", "2023-04-06", "2023-12-03", latest_date]},
            {"x": ["2023-02-05", "2023-08-03", "2023-12-19"]},
        ]
        mocked_figure = mock.Mock(data=data)

        # When
        last_x_value = (
            reporting_delay_period._get_last_x_value_at_end_of_reporting_delay_period(
                figure=mocked_figure
            )
        )

        # Then
        assert last_x_value == latest_date


class TestAddReportingDelayPeriod:
    @mock.patch(f"{MODULE_PATH}._get_last_x_value_at_end_of_reporting_delay_period")
    @mock.patch(f"{MODULE_PATH}._get_x_value_at_start_of_reporting_delay_period")
    def test_draws_vertical_filled_region(
        self,
        mocked_get_x_value_at_start_of_reporting_delay_period: mock.MagicMock,
        mocked_get_last_x_value_at_end_of_reporting_delay_period: mock.MagicMock,
    ):
        """
        Given start and end X date values
        When `add_reporting_delay_period()` is called
        Then the `add_vrect()` method is called
            on the plotly figure with the correct args
        """
        # Given
        mocked_figure = mock.Mock()
        start_x = "2024-01-01"
        end_x = "2024-02-01"
        mocked_get_x_value_at_start_of_reporting_delay_period.return_value = start_x
        mocked_get_last_x_value_at_end_of_reporting_delay_period.return_value = end_x

        # When
        reporting_delay_period.add_reporting_delay_period(
            chart_plots_data=mock.Mock(), figure=mocked_figure
        )

        # Then
        mocked_figure.add_vrect.assert_called_once_with(
            x0=start_x,
            x1=end_x,
            fillcolor=reporting_delay_period.LIGHT_BLUE,
            opacity=0.6,
            line_width=0,
        )

    @mock.patch(f"{MODULE_PATH}._get_last_x_value_at_end_of_reporting_delay_period")
    @mock.patch(f"{MODULE_PATH}._get_x_value_at_start_of_reporting_delay_period")
    def test_draws_vertical_boundaries(
        self,
        mocked_get_x_value_at_start_of_reporting_delay_period: mock.MagicMock,
        mocked_get_last_x_value_at_end_of_reporting_delay_period: mock.MagicMock,
    ):
        """
        Given start and end X date values
        When `add_reporting_delay_period()` is called
        Then the `add_vline()` method is called
            on the plotly figure with the correct args
            for each of the boundary lines
        """
        # Given
        mocked_figure = mock.Mock()
        start_x = "2024-01-01"
        end_x = "2024-02-01"
        mocked_get_x_value_at_start_of_reporting_delay_period.return_value = start_x
        mocked_get_last_x_value_at_end_of_reporting_delay_period.return_value = end_x

        # When
        reporting_delay_period.add_reporting_delay_period(
            chart_plots_data=mock.Mock(), figure=mocked_figure
        )

        # Then
        expected_calls = [
            mock.call(x=start_x, line_color=reporting_delay_period.CYAN, line_width=2),
            mock.call(x=end_x, line_color=reporting_delay_period.CYAN, line_width=2),
        ]

        mocked_figure.add_vline.assert_has_calls(calls=expected_calls, any_order=True)

    @mock.patch(f"{MODULE_PATH}._get_last_x_value_at_end_of_reporting_delay_period")
    @mock.patch(f"{MODULE_PATH}._get_x_value_at_start_of_reporting_delay_period")
    def test_adds_trace_for_legend(
        self,
        mocked_get_x_value_at_start_of_reporting_delay_period: mock.MagicMock,
        mocked_get_last_x_value_at_end_of_reporting_delay_period: mock.MagicMock,
    ):
        """
        Given a figure
        When `add_reporting_delay_period()` is called
        Then the `add_trace()` method is called
            on the plotly figure with the correct args
            for the dummy trace required to render
            the reporting delay period on the legend
        """
        # Given
        mocked_figure = mock.Mock()
        start_x = "2024-01-01"
        end_x = "2024-02-01"
        mocked_get_x_value_at_start_of_reporting_delay_period.return_value = start_x
        mocked_get_last_x_value_at_end_of_reporting_delay_period.return_value = end_x

        # When
        reporting_delay_period.add_reporting_delay_period(
            chart_plots_data=mock.Mock(), figure=mocked_figure
        )

        # Then
        expected_scatter = Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={
                "color": reporting_delay_period.LIGHT_BLUE,
                "opacity": 0.6,
                "symbol": "square",
                "size": 15,
                "line": {"color": reporting_delay_period.CYAN, "width": 2},
            },
            name="Reporting delay",
        )

        mocked_figure.add_trace.assert_called_once_with(trace=expected_scatter)

    @pytest.mark.parametrize("additional_values", [{}, None])
    def test_does_not_draw_section_when_no_reporting_delay_period_found(
        self,
        fake_plot_data: PlotData,
        additional_values: dict | None,
    ):
        """
        Given an enriched `PlotData` model
            which contains nothing for its
            `additional_values`
        When `add_reporting_delay_period()` is called
        Then the section is not drawn
        """
        # Given
        mocked_figure = mock.Mock()
        fake_plot_data.additional_values = additional_values

        # When
        reporting_delay_period.add_reporting_delay_period(
            chart_plots_data=[fake_plot_data],
            figure=mocked_figure,
        )

        # Then
        mocked_figure.add_vrect.assert_not_called()
        mocked_figure.add_vline.assert_not_called()

    def test_does_not_draw_section_when_reporting_delay_period_contains_no_valid_start_point(
        self, fake_plot_data: PlotData
    ):
        """
        Given an enriched `PlotData` model
            which contains a list of reporting delay period values
            which do not have 1 True value
        When `add_reporting_delay_period()` is called
        Then the section is not drawn
        """
        # Given
        mocked_figure = mock.Mock()
        fake_plot_data.additional_values = {"in_reporting_delay_period": [False] * 10}

        # When
        reporting_delay_period.add_reporting_delay_period(
            chart_plots_data=[fake_plot_data],
            figure=mocked_figure,
        )

        # Then
        mocked_figure.add_vrect.assert_not_called()
        mocked_figure.add_vline.assert_not_called()
