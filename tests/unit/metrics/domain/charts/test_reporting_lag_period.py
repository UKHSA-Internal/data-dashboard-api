from unittest import mock
from metrics.domain.charts import reporting_lag_period
from metrics.domain.charts.reporting_lag_period import add_reporting_lag_period

MODULE_PATH = "metrics.domain.charts.reporting_lag_period"


class TestGetLastXValueAtEndOfReportingLagPeriod:
    def test_returns_last_x_value_in_plots(self):
        """
        Given a figure which contains plots with various dates
        When `_get_last_x_value_at_end_of_reporting_lag_period()` is called
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
            reporting_lag_period._get_last_x_value_at_end_of_reporting_lag_period(
                figure=mocked_figure
            )
        )

        # Then
        assert last_x_value == latest_date


class TestAddReportingLagPeriod:
    @mock.patch(f"{MODULE_PATH}._get_last_x_value_at_end_of_reporting_lag_period")
    @mock.patch(f"{MODULE_PATH}._get_x_value_at_start_of_reporting_lag_period")
    def test_draws_vertical_filled_region(
        self,
        mocked_get_x_value_at_start_of_reporting_lag_period: mock.MagicMock,
        mocked_get_last_x_value_at_end_of_reporting_lag_period: mock.MagicMock,
    ):
        """
        Given start and end X date values
        When `add_reporting_lag_period()` is called
        Then the `add_vrect()` method is called
            on the plotly figure with the correct args
        """
        # Given
        mocked_figure = mock.Mock()
        start_x = "2024-01-01"
        end_x = "2024-02-01"
        mocked_get_x_value_at_start_of_reporting_lag_period.return_value = start_x
        mocked_get_last_x_value_at_end_of_reporting_lag_period.return_value = end_x

        # When
        add_reporting_lag_period(chart_plots_data=mock.Mock(), figure=mocked_figure)

        # Then
        mocked_figure.add_vrect.assert_called_once_with(
            x0=start_x,
            x1=end_x,
            fillcolor=reporting_lag_period.LIGHT_BLUE,
            opacity=0.6,
            line_width=0,
        )

    @mock.patch(f"{MODULE_PATH}._get_last_x_value_at_end_of_reporting_lag_period")
    @mock.patch(f"{MODULE_PATH}._get_x_value_at_start_of_reporting_lag_period")
    def test_draws_vertical_boundaries(
        self,
        mocked_get_x_value_at_start_of_reporting_lag_period: mock.MagicMock,
        mocked_get_last_x_value_at_end_of_reporting_lag_period: mock.MagicMock,
    ):
        """
        Given start and end X date values
        When `add_reporting_lag_period()` is called
        Then the `add_vline()` method is called
            on the plotly figure with the correct args
            for each of the boundary lines
        """
        # Given
        mocked_figure = mock.Mock()
        start_x = "2024-01-01"
        end_x = "2024-02-01"
        mocked_get_x_value_at_start_of_reporting_lag_period.return_value = start_x
        mocked_get_last_x_value_at_end_of_reporting_lag_period.return_value = end_x

        # When
        add_reporting_lag_period(chart_plots_data=mock.Mock(), figure=mocked_figure)

        # Then
        expected_calls = [
            mock.call(x=start_x, line_color=reporting_lag_period.CYAN, line_width=2),
            mock.call(x=end_x, line_color=reporting_lag_period.CYAN, line_width=2),
        ]

        mocked_figure.add_vline.assert_has_calls(calls=expected_calls, any_order=True)
