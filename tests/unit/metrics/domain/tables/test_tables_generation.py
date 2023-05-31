import datetime
from typing import List

from metrics.domain.models import PlotParameters, PlotsData
from metrics.domain.tables.generation import (
    combine_list_of_plots,
    create_plots_in_tabular_format,
    generate_multi_plot_output,
)

TEST_PLOT = "Test Plot"

X_AXIS_VALUES = [
    datetime.date(2022, 9, 5),
    datetime.date(2022, 9, 19),
]
Y_AXIS_1_VALUES = [10, 22]
Y_AXIS_2_VALUES = [20, 45]

PLOT_1_LABEL = "0 to 4 years old"
PLOT_2_LABEL = "15 to 44 years old"


def _create_plot_data(
    x_axis_values: List[datetime.date],
    y_axis_values: List[int],
    label: str = "",
) -> PlotsData:
    plot_params = PlotParameters(
        chart_type="",
        topic="RSV",
        metric="weekly_positivity_by_age",
        stratum="0_4",
        label=label,
    )
    return PlotsData(
        parameters=plot_params,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
    )


class TestCombinePlots:
    def test_basic_combine_list_of_plots(self):
        """
        Given 2 `TabularPlotData` models representing 2 different line plots
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_1_VALUES,
            label=PLOT_1_LABEL,
        )

        second_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_2_VALUES,
            label=PLOT_2_LABEL,
        )

        expected_combined_plots = {
            "2022-09-30": {PLOT_1_LABEL: "22", PLOT_2_LABEL: "45"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            tabular_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check plot labels are as expected
        assert len(plot_labels) == 2
        assert plot_labels[0] == PLOT_1_LABEL
        assert plot_labels[1] == PLOT_2_LABEL

        # Check combined plot output is as expected
        assert combined_plots == expected_combined_plots

    def test_combine_list_of_plots_no_labels(self):
        """
        Given 2 `TabularPlotData` models representing 2 different line plots without labels
        When `combine_list_of_plots()` is called
        Then labels are automatically assigned
        """
        # Given
        first_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_1_VALUES,
        )
        second_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_2_VALUES,
        )
        expected_combined_plots = {
            "2022-09-30": {"Plot1": "22", "Plot2": "45"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            tabular_plots_data=[first_chart_plots_data, second_chart_plots_data],
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
        Given 2 `TabularPlotData` models representing 2 different line plots of unequal lengths
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = _create_plot_data(
            x_axis_values=[
                datetime.date(2022, 8, 5),
                datetime.date(2022, 9, 6),
                datetime.date(2022, 10, 19),
                datetime.date(2022, 11, 25),
            ],
            y_axis_values=[10, 66, 22, 26],
            label=PLOT_1_LABEL,
        )

        second_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_2_VALUES,
            label=PLOT_2_LABEL,
        )

        expected_combined_plots = {
            "2022-08-31": {PLOT_1_LABEL: "10"},
            "2022-09-30": {PLOT_1_LABEL: "66", PLOT_2_LABEL: "45"},
            "2022-10-31": {PLOT_1_LABEL: "22"},
            "2022-11-30": {PLOT_1_LABEL: "26"},
        }

        # When
        plot_labels, combined_plots = combine_list_of_plots(
            tabular_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check plot labels are as expected
        assert len(plot_labels) == 2
        assert plot_labels[0] == PLOT_1_LABEL
        assert plot_labels[1] == PLOT_2_LABEL

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
            "2022-09-06": {"Plot1": "06", "Plot2": "63"},
        }

        expected_output = [
            {
                "date": "2022-09-05",
                "values": [
                    {"label": "Plot1", "value": "10"},
                    {"label": "Plot2", "value": "11"},
                ],
            },
            {
                "date": "2022-09-06",
                "values": [
                    {"label": "Plot1", "value": "06"},
                    {"label": "Plot2", "value": "63"},
                ],
            },
            {
                "date": "2022-09-19",
                "values": [
                    {"label": "Plot1", "value": "22"},
                    {"label": "Plot2", "value": "33"},
                ],
            },
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
            "2022-09-06": {"Plot2": "06"},
        }
        expected_output = [
            {
                "date": "2022-09-05",
                "values": [
                    {"label": "Plot1", "value": "10"},
                    {"label": "Plot2", "value": None},
                ],
            },
            {
                "date": "2022-09-06",
                "values": [
                    {"label": "Plot1", "value": None},
                    {"label": "Plot2", "value": "06"},
                ],
            },
            {
                "date": "2022-09-19",
                "values": [
                    {"label": "Plot1", "value": "22"},
                    {"label": "Plot2", "value": "33"},
                ],
            },
            {
                "date": "2022-09-25",
                "values": [
                    {"label": "Plot1", "value": None},
                    {"label": "Plot2", "value": "44"},
                ],
            },
        ]

        # When
        actual_output = generate_multi_plot_output(
            plot_labels=plot_labels, combined_plots=combined_plots
        )

        # Then
        assert actual_output == expected_output


class TestCreatePlotsInTabularFormat:
    def test_two_plots_with_provided_labels(self):
        """
        Given 2 `ChartPlotData` models representing 2 different line plots
        When `generate_plots_for_table()` is called from the `tables` module
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_1_VALUES,
            label=PLOT_1_LABEL,
        )

        second_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_2_VALUES,
            label=PLOT_2_LABEL,
        )

        expected_x_axis_values = ["2022-09-30"]

        # When
        actual_output = create_plots_in_tabular_format(
            tabular_plots_data=[first_chart_plots_data, second_chart_plots_data],
        )

        # Then
        # Check the number of plots is as expected.
        # Examine just the fist and last elements
        assert len(actual_output[0]["values"]) == 2
        assert len(actual_output[len(actual_output) - 1]["values"]) == 2

        # Check the x axis values match
        actual_x_axis_values = [col["date"] for col in actual_output]
        assert expected_x_axis_values == actual_x_axis_values
