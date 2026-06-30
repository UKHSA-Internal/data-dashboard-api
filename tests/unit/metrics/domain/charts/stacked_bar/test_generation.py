from unittest import mock

import plotly.graph_objects as go

from metrics.domain.charts.stacked_bar.generation import generate_stacked_bar
from metrics.domain.models.plots import ChartGenerationPayload, PlotGenerationData

MODULE_PATH = "metrics.domain.charts.stacked_bar.generation"

HEIGHT = 400
WIDTH = 640


class TestGenerateStackedBar:
    @mock.patch(f"{MODULE_PATH}.add_reporting_delay_period")
    def test_adds_reporting_delay_period_when_x_axis_is_date_type(
        self,
        mocked_add_reporting_delay_period: mock.MagicMock,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given stacked bar plot data with date values on the x-axis
        When `generate_stacked_bar()` is called
        Then the reporting delay period is added to the figure
        """
        # Given
        fake_plot_data.parameters.chart_type = "stacked_bar"
        fake_plot_data.parameters.age = "all"

        # Adding in_reporting_delay_period to the last date in the x-axis values
        fake_plot_data.additional_values = {
            "in_reporting_delay_period": [False]
            * (len(fake_plot_data.x_axis_values) - 1)
            + [True],
        }
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=[fake_plot_data],
            x_axis_title="Date",
            y_axis_title="Cases",
            secondary_category="age",
        )

        # When
        figure = generate_stacked_bar(chart_generation_payload=chart_payload)

        # Then
        mocked_add_reporting_delay_period.assert_called_once_with(
            chart_plots_data=chart_payload.plots,
            figure=figure,
        )
        assert isinstance(figure, go.Figure)
        assert len(figure.data) == 1

    @mock.patch(f"{MODULE_PATH}.add_reporting_delay_period")
    def test_does_not_add_reporting_delay_period_when_x_axis_is_not_date_type(
        self,
        mocked_add_reporting_delay_period: mock.MagicMock,
        fake_plot_data: PlotGenerationData,
    ):
        """
        Given stacked bar plot data with non-date values on the x-axis
        When `generate_stacked_bar()` is called
        Then the reporting delay period is not added to the figure
        """
        # Given
        fake_plot_data.parameters.chart_type = "stacked_bar"
        fake_plot_data.parameters.age = "all"
        fake_plot_data.x_axis_values = ["0-4", "5-9", "10-14"]
        fake_plot_data.y_axis_values = fake_plot_data.y_axis_values[
            : len(fake_plot_data.x_axis_values)
        ]
        chart_payload = ChartGenerationPayload(
            chart_width=WIDTH,
            chart_height=HEIGHT,
            plots=[fake_plot_data],
            x_axis_title="Age",
            y_axis_title="Cases",
            secondary_category="age",
        )

        # When
        generate_stacked_bar(chart_generation_payload=chart_payload)

        # Then
        mocked_add_reporting_delay_period.assert_not_called()
