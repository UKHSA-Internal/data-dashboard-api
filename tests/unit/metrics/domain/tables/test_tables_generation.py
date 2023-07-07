import datetime
from typing import Any
from unittest import mock

from metrics.domain.models import PlotData, PlotParameters
from metrics.domain.tables.generation import TabularData

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
    x_axis_values: list[Any],
    y_axis_values: list[Any],
    label: str = "",
    x_axis: str = "",
) -> PlotData:
    plot_params = PlotParameters(
        chart_type="",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
        stratum="default",
        label=label,
        x_axis=x_axis,
    )
    return PlotData(
        parameters=plot_params,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
    )


class TestTabularData:
    @mock.patch.object(TabularData, "combine_list_of_plots")
    @mock.patch.object(TabularData, "generate_multi_plot_output")
    def test_delegates_call_for_validation(
        self,
        spy_generate_multi_plot_output: mock.MagicMock,
        spy_combine_list_of_plots: mock.MagicMock,
    ):
        """
        Given a mock in place of a `PlotData` model
        When `create_plots_in_tabular_format()` is called
        Then a call is delegated to `combine_list_of_plots()` to combine the plots
        And `generate_plots_for_table` is called to produce the output in the required format

        Patches:
            `spy_generate_multi_plot_output`: For the main collation
            `spy_combine_list_of_plots`: For combining the plots
        """
        # Given
        mocked_plots = mock.MagicMock()

        # When
        mock_tabular_data = TabularData(plots=mocked_plots)

        plots_in_tabular_format = mock_tabular_data.create_plots_in_tabular_format()

        # Then
        spy_combine_list_of_plots.assert_called_once()
        spy_generate_multi_plot_output.assert_called_once()
        assert plots_in_tabular_format == spy_generate_multi_plot_output.return_value


class TestCollateDataByDate:
    def test_basic_behaviour(self):
        """
        Given a plot which is by date
        When `collate_data_by_date()` is called
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = dict(zip(X_AXIS_VALUES, Y_AXIS_1_VALUES))

        expected_combined_plots = {"2022-09-30": {PLOT_1_LABEL: "22"}}

        # When
        tabular_data = TabularData(plots=[])

        tabular_data.collate_data_by_date(
            plot_data=first_chart_plots_data,
            plot_label=PLOT_1_LABEL,
        )

        # Then
        assert tabular_data.combined_plots == expected_combined_plots

    def test_two_plots(self):
        """
        Given two plot which are both by date
        When `collate_data_by_date()` is called
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = dict(zip(X_AXIS_VALUES, Y_AXIS_1_VALUES))
        second_chart_plots_data = dict(zip(X_AXIS_VALUES, Y_AXIS_2_VALUES))
        tabular_data = TabularData(plots=[])

        # When
        tabular_data.collate_data_by_date(
            plot_data=first_chart_plots_data,
            plot_label=PLOT_1_LABEL,
        )
        tabular_data.collate_data_by_date(
            plot_data=second_chart_plots_data,
            plot_label=PLOT_2_LABEL,
        )
        expected_combined_plots = {
            "2022-09-30": {PLOT_1_LABEL: "22", PLOT_2_LABEL: "45"},
        }

        # Then
        assert tabular_data.combined_plots == expected_combined_plots


class TestCollateDataNotByDate:
    def test_basic_behaviour(self):
        """
        Given a plot which is not by date
        When `collate_data_not_by_date()` is called
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = dict(zip(["0-4", "5-8"], Y_AXIS_1_VALUES))

        expected_combined_plots = {
            "0-4": {PLOT_1_LABEL: "10"},
            "5-8": {PLOT_1_LABEL: "22"},
        }

        # When
        tabular_data = TabularData(plots=[])

        tabular_data.collate_data_not_by_date(
            plot_data=first_chart_plots_data,
            plot_label=PLOT_1_LABEL,
        )

        # Then
        assert tabular_data.combined_plots == expected_combined_plots

    def test_two_plots(self):
        """
        Given two plot neither of which are by date
        When `collate_data_not_by_date()` is called
        Then the correct response is generated
        """
        first_chart_plots_data = dict(zip(["0-4", "5-8"], Y_AXIS_1_VALUES))
        second_chart_plots_data = dict(zip(["0-4", "5-8"], Y_AXIS_2_VALUES))

        expected_combined_plots = {
            "0-4": {PLOT_1_LABEL: "10", PLOT_2_LABEL: "20"},
            "5-8": {PLOT_1_LABEL: "22", PLOT_2_LABEL: "45"},
        }

        # When
        tabular_data = TabularData(plots=[])

        tabular_data.collate_data_not_by_date(
            plot_data=first_chart_plots_data,
            plot_label=PLOT_1_LABEL,
        )
        tabular_data.collate_data_not_by_date(
            plot_data=second_chart_plots_data,
            plot_label=PLOT_2_LABEL,
        )

        # Then
        assert tabular_data.combined_plots == expected_combined_plots


class TestCombineListOfPlots:
    def test_plots_have_dates(self):
        """
        Given 2 `TabularPlotData` models representing 2 different line plots
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data: PlotData = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_1_VALUES,
            label=PLOT_1_LABEL,
            x_axis="date",
        )

        second_chart_plots_data: PlotData = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_2_VALUES,
            label=PLOT_2_LABEL,
            x_axis="date",
        )

        expected_combined_plots = {
            "2022-09-30": {PLOT_1_LABEL: "22", PLOT_2_LABEL: "45"},
        }

        # When
        tabular_data = TabularData(
            plots=[first_chart_plots_data, second_chart_plots_data]
        )

        tabular_data.combine_list_of_plots()

        # Then
        # Check plot labels are as expected
        assert tabular_data.column_heading == "date"
        assert len(tabular_data.plot_labels) == 2
        assert tabular_data.plot_labels[0] == PLOT_1_LABEL
        assert tabular_data.plot_labels[1] == PLOT_2_LABEL

        # Check combined plot output is as expected
        assert tabular_data.combined_plots == expected_combined_plots

    def test_plots_do_not_have_dates(self):
        """
        Given 2 `TabularPlotData` models representing 2 different line plots
         where neither plot has dates
        When `combine_list_of_plots()` is called
        Then the correct response is generated
        """
        # Given
        X_AXIS_STRATUM = ["0-4", "5-8"]

        first_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_STRATUM,
            y_axis_values=Y_AXIS_1_VALUES,
            label=PLOT_1_LABEL,
            x_axis="stratum",
        )

        second_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_STRATUM,
            y_axis_values=Y_AXIS_2_VALUES,
            label=PLOT_2_LABEL,
            x_axis="stratum",
        )

        expected_combined_plots = {
            "0-4": {PLOT_1_LABEL: "10", PLOT_2_LABEL: "20"},
            "5-8": {PLOT_1_LABEL: "22", PLOT_2_LABEL: "45"},
        }

        # When
        tabular_data = TabularData(
            plots=[first_chart_plots_data, second_chart_plots_data]
        )

        tabular_data.combine_list_of_plots()

        # Then
        # Check plot labels are as expected
        assert tabular_data.column_heading == "stratum"
        assert len(tabular_data.plot_labels) == 2
        assert tabular_data.plot_labels[0] == PLOT_1_LABEL
        assert tabular_data.plot_labels[1] == PLOT_2_LABEL

        # Check combined plot output is as expected
        assert tabular_data.combined_plots == expected_combined_plots

    def test_plots_have_no_labels(self):
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
        tabular_data = TabularData(
            plots=[first_chart_plots_data, second_chart_plots_data]
        )
        tabular_data.combine_list_of_plots()

        # Then
        # Check plot labels are as expected
        assert len(tabular_data.plot_labels) == 2
        assert tabular_data.plot_labels[0] == "Plot1"
        assert tabular_data.plot_labels[1] == "Plot2"

        # Check combined plot output is as expected
        assert tabular_data.combined_plots == expected_combined_plots

    def test_plots_have_different_lengths(self):
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
        tabular_data = TabularData(
            plots=[first_chart_plots_data, second_chart_plots_data]
        )
        tabular_data.combine_list_of_plots()

        # Then
        # Check plot labels are as expected
        assert len(tabular_data.plot_labels) == 2
        assert tabular_data.plot_labels[0] == PLOT_1_LABEL
        assert tabular_data.plot_labels[1] == PLOT_2_LABEL

        # Check combined plot output is as expected
        assert tabular_data.combined_plots == expected_combined_plots


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
        tabular_data = TabularData(plots=[])
        tabular_data.plot_labels = plot_labels
        tabular_data.combined_plots = combined_plots
        tabular_data.column_heading = "date"
        actual_output = tabular_data.generate_multi_plot_output()

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
        tabular_data = TabularData(plots=[])
        tabular_data.plot_labels = plot_labels
        tabular_data.combined_plots = combined_plots
        tabular_data.column_heading = "date"
        actual_output = tabular_data.generate_multi_plot_output()

        # Then
        assert actual_output == expected_output


class TestCreatePlotsInTabularFormat:
    def test_two_plots_with_provided_labels(self):
        """
        Given 2 `PlotData` models representing 2 different line plots
        When `generate_plots_for_table()` is called from the `TabularData` module
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_1_VALUES,
            label=PLOT_1_LABEL,
            x_axis="date",
        )

        second_chart_plots_data = _create_plot_data(
            x_axis_values=X_AXIS_VALUES,
            y_axis_values=Y_AXIS_2_VALUES,
            label=PLOT_2_LABEL,
            x_axis="date",
        )

        expected_x_axis_values = ["2022-09-30"]

        # When
        tabular_data = TabularData(
            plots=[first_chart_plots_data, second_chart_plots_data]
        )
        actual_output = tabular_data.create_plots_in_tabular_format()

        # Then
        # Check the number of plots is as expected.
        # Examine just the fist and last elements
        assert len(actual_output[0]["values"]) == 2
        assert len(actual_output[len(actual_output) - 1]["values"]) == 2

        # Check the x axis values match
        actual_x_axis_values = [col["date"] for col in actual_output]
        assert expected_x_axis_values == actual_x_axis_values
