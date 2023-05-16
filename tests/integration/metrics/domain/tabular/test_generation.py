import datetime
from typing import List

from metrics.domain.models import ChartPlotData, ChartPlotParameters
from metrics.domain.tabular.generation import create_plots_in_tabular_format

DATES_FROM_SEP_TO_OCT: List[datetime.datetime] = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 9, 19),
    datetime.date(2022, 10, 3),
]
EXAMPLE_VALUES: List[int] = [10, 22, 8]


class TestTabularInterface:
    @staticmethod
    def _setup_chart_plot_data(
        x_axis: List[datetime.date],
        y_axis: List[int],
        label: str = "",
        line_type: str = "",
        line_colour: str = "",
    ) -> ChartPlotData:
        plot_params = ChartPlotParameters(
            chart_type="line_multi_coloured",
            topic="RSV",
            metric="weekly_positivity_by_age",
            stratum="0_4",
            label=label,
            line_type=line_type,
            line_colour=line_colour,
        )
        return ChartPlotData(parameters=plot_params, x_axis=x_axis, y_axis=y_axis)

    def test_single_plot(self):
        """
        Given a `ChartPlotData` models representing a line plot
        When `generate_plots_for_table()` is called from the `tabular` module
        Then the correct response is generated
        """
        # Given
        dates = DATES_FROM_SEP_TO_OCT
        values = EXAMPLE_VALUES
        chart_plots_data = self._setup_chart_plot_data(x_axis=dates, y_axis=values)
        expected_x_axis_values = [
            dt.strftime("%Y-%m-%d") for dt in DATES_FROM_SEP_TO_OCT
        ]
        expected_y_axis_values = [str(val) for val in EXAMPLE_VALUES]

        # When
        actual_output = create_plots_in_tabular_format(
            chart_plots_data=[chart_plots_data]
        )

        # Then
        # Check basic length of output
        assert len(DATES_FROM_SEP_TO_OCT) == len(actual_output)
        assert len(EXAMPLE_VALUES) == len(actual_output)

        # Check the x axis values match
        actual_x_axis_values = [col["date"] for col in actual_output]
        assert expected_x_axis_values == actual_x_axis_values

        # Check the y axis values match
        actual_y_axis_values = [col["Plot1"] for col in actual_output]
        assert expected_y_axis_values == actual_y_axis_values

    def test_two_plots_with_provided_labels(self):
        """
        Given 2 `ChartPlotData` models representing 2 different line plots
        When `generate_plots_for_table()` is called from the `tabular` module
        Then the correct response is generated
        """
        # Given
        dates = DATES_FROM_SEP_TO_OCT
        values_plot1 = EXAMPLE_VALUES
        first_plot_line_type = "DASH"
        first_plot_label = "0 to 4 years old"
        first_plot_colour = "RED"
        first_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot1,
            label=first_plot_label,
            line_type=first_plot_line_type,
            line_colour=first_plot_colour,
        )

        dates = DATES_FROM_SEP_TO_OCT
        second_plot_line_type = "SOLID"
        second_plot_label = "15 to 44 years old"
        values_plot2 = [20, 45, 62]
        second_plot_colour = "BLUE"
        second_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot2,
            label=second_plot_label,
            line_type=second_plot_line_type,
            line_colour=second_plot_colour,
        )
        expected_x_axis_values = [
            dt.strftime("%Y-%m-%d") for dt in DATES_FROM_SEP_TO_OCT
        ]

        # When
        actual_output = create_plots_in_tabular_format(
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check basic length of output
        assert len(DATES_FROM_SEP_TO_OCT) == len(actual_output)

        # Check the number of plots is as expected.
        # Examine just the fist and last elements
        assert len(actual_output[0]["values"]) == 2
        assert len(actual_output[len(actual_output) - 1]["values"]) == 2

        # Check the x axis values match
        actual_x_axis_values = [col["date"] for col in actual_output]
        assert expected_x_axis_values == actual_x_axis_values

        # Check the first plot
        actual_y_axis_values = [
            col["values"][first_plot_label] for col in actual_output
        ]
        expected_y_axis_values = [str(val) for val in values_plot1]
        assert expected_y_axis_values == actual_y_axis_values

        # Check the second plot
        actual_y_axis_values = [
            col["values"][second_plot_label] for col in actual_output
        ]
        expected_y_axis_values = [str(val) for val in values_plot2]
        assert expected_y_axis_values == actual_y_axis_values
