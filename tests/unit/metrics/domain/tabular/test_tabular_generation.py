import datetime
from typing import List

from metrics.domain.models import ChartPlotData, ChartPlotParameters
from metrics.domain.tabular.generation import (
    combine_list_of_plots,
    generate_multi_plot_output,
    generate_single_plot_output,
)


class TestCombinePlots:
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
        Given 1 `ChartPlotData` model representing a line plot
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        dates = [
            datetime.date(2022, 9, 5),
            datetime.date(2022, 9, 19),
        ]

        plot_line_type = "DASH"
        plot_label = "0 to 4 years old"
        values_plot = [10, 22]
        plot_colour = "RED"
        chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot,
            label=plot_label,
            line_type=plot_line_type,
            line_colour=plot_colour,
        )

        expected_combined_plots = {
            "2022-09-05": {"0 to 4 years old": "10"},
            "2022-09-19": {"0 to 4 years old": "22"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            chart_plots_data=[chart_plots_data],
        )

        # Then
        # Check plot labels are as expected
        assert len(plot_labels) == 1
        assert plot_labels == [plot_label]

        # Check combined plot output is as expected
        assert combined_plots == expected_combined_plots

    def test_basic_combine_list_of_plots(self):
        """
        Given 2 `ChartPlotData` models representing 2 different line plots
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        dates = [
            datetime.date(2022, 9, 5),
            datetime.date(2022, 9, 19),
        ]

        first_plot_line_type = "DASH"
        first_plot_label = "0 to 4 years old"
        values_plot1 = [10, 22]
        first_plot_colour = "RED"
        first_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot1,
            label=first_plot_label,
            line_type=first_plot_line_type,
            line_colour=first_plot_colour,
        )

        second_plot_line_type = "SOLID"
        second_plot_label = "15 to 44 years old"
        values_plot2 = [20, 45]
        second_plot_colour = "BLUE"
        second_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot2,
            label=second_plot_label,
            line_type=second_plot_line_type,
            line_colour=second_plot_colour,
        )

        expected_combined_plots = {
            "2022-09-05": {"0 to 4 years old": "10", "15 to 44 years old": "20"},
            "2022-09-19": {"0 to 4 years old": "22", "15 to 44 years old": "45"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check plot labels are as expected
        assert len(plot_labels) == 2
        assert plot_labels[0] == first_plot_label
        assert plot_labels[1] == second_plot_label

        # Check combined plot output is as expected
        assert combined_plots == expected_combined_plots

    def test_combine_list_of_plots_no_labels(self):
        """
        Given 2 `ChartPlotData` models representing 2 different line plots without labels
        When `combine_list_of_plots()` is called
        Then labels are automatically assigned
        """
        # Given
        dates = [
            datetime.date(2022, 9, 5),
            datetime.date(2022, 9, 19),
        ]

        first_plot_line_type = "DASH"
        values_plot1 = [10, 22]
        first_plot_colour = "RED"
        first_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot1,
            line_type=first_plot_line_type,
            line_colour=first_plot_colour,
        )

        second_plot_line_type = "SOLID"
        values_plot2 = [20, 45]
        second_plot_colour = "BLUE"
        second_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot2,
            line_type=second_plot_line_type,
            line_colour=second_plot_colour,
        )

        expected_combined_plots = {
            "2022-09-05": {"Plot1": "10", "Plot2": "20"},
            "2022-09-19": {"Plot1": "22", "Plot2": "45"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check plot labels are as expected
        assert len(plot_labels) == 2
        assert plot_labels[0] == "Plot1"
        assert plot_labels[1] == "Plot2"

        # Check combined plot output is as expected
        assert combined_plots == expected_combined_plots

    def test_different_length_combine_list_of_plots(self):
        """
        Given 2 `ChartPlotData` models representing 2 different line plots of unequal lengths
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        dates = [
            datetime.date(2022, 9, 5),
            datetime.date(2022, 9, 19),
            datetime.date(2022, 9, 25),
        ]

        first_plot_line_type = "DASH"
        first_plot_label = "0 to 4 years old"
        values_plot1 = [10, 22, 26]
        first_plot_colour = "RED"
        first_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot1,
            label=first_plot_label,
            line_type=first_plot_line_type,
            line_colour=first_plot_colour,
        )

        second_plot_line_type = "SOLID"
        second_plot_label = "15 to 44 years old"
        values_plot2 = [20, 45]
        second_plot_colour = "BLUE"
        second_chart_plots_data = self._setup_chart_plot_data(
            x_axis=dates,
            y_axis=values_plot2,
            label=second_plot_label,
            line_type=second_plot_line_type,
            line_colour=second_plot_colour,
        )

        expected_combined_plots = {
            "2022-09-05": {"0 to 4 years old": "10", "15 to 44 years old": "20"},
            "2022-09-19": {"0 to 4 years old": "22", "15 to 44 years old": "45"},
            "2022-09-25": {"0 to 4 years old": "26"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            chart_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check plot labels are as expected
        assert len(plot_labels) == 2
        assert plot_labels[0] == first_plot_label
        assert plot_labels[1] == second_plot_label

        # Check combined plot output is as expected
        assert combined_plots == expected_combined_plots


class TestGenerateMultiPlotOutput:
    def test_basic_generate_multi_plot_output(self):
        """
        Given 2 plots with plot labels
        When `generate_multi_plot_output()` is called
        Then the correct response is generated
        """
        # Given
        plot_labels = ["Plot1", "Plot2"]
        combined_plots = {
            "2022-09-05": {"Plot1": "10", "Plot2": "11"},
            "2022-09-19": {"Plot1": "22", "Plot2": "33"},
        }

        expected_output = [
            {"date": "2022-09-05", "values": {"Plot1": "10", "Plot2": "11"}},
            {"date": "2022-09-19", "values": {"Plot1": "22", "Plot2": "33"}},
        ]

        # When
        actual_output = generate_multi_plot_output(
            plot_labels=plot_labels, combined_plots=combined_plots
        )

        # Then
        assert actual_output == expected_output

    def test_generate_multi_plot_output_unequal_length(self):
        """
        Given 2 plots which are not the same length as each other
        When `generate_multi_plot_output()` is called
        Then the correct response is generated
        """
        # Given
        plot_labels = ["Plot1", "Plot2"]
        combined_plots = {
            "2022-09-05": {"Plot1": "10"},
            "2022-09-19": {"Plot1": "22", "Plot2": "33"},
            "2022-09-25": {"Plot2": "44"},
        }

        expected_output = [
            {"date": "2022-09-05", "values": {"Plot1": "10", "Plot2": "-"}},
            {"date": "2022-09-19", "values": {"Plot1": "22", "Plot2": "33"}},
            {"date": "2022-09-25", "values": {"Plot1": "-", "Plot2": "44"}},
        ]

        # When
        actual_output = generate_multi_plot_output(
            plot_labels=plot_labels, combined_plots=combined_plots
        )

        # Then
        assert actual_output == expected_output


class TestGenerateSinglePlotOutput:
    def test_basic_generate_single_plot_output(self):
        """
        Given 1 plots
        When `generate_single_plot_output()` is called
        Then the correct response is generated
        """
        # Given
        plot_data = {
            "2022-09-05": {"Test Plot": "10"},
            "2022-09-19": {"Test Plot": "22"},
        }

        expected_output = [
            {"date": "2022-09-05", "Test Plot": "10"},
            {"date": "2022-09-19", "Test Plot": "22"},
        ]

        # When
        actual_output = generate_single_plot_output(plot_data=plot_data)

        # Then
        assert actual_output == expected_output
