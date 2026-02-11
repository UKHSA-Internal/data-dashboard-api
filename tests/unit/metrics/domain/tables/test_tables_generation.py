import datetime
from decimal import Decimal
from typing import Any

import pytest

from metrics.domain.models import PlotGenerationData, PlotParameters
from metrics.domain.tables.generation import (
    LOWER_CONFIDENCE,
    TabularData,
    UPPER_CONFIDENCE,
)
from metrics.domain.common.utils import ChartAxisFields

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
) -> PlotGenerationData:
    plot_params = PlotParameters(
        chart_type="",
        topic="COVID-19",
        metric="COVID-19_deaths_ONSByDay",
        stratum="default",
        label=label,
        x_axis=x_axis,
    )
    return PlotGenerationData(
        parameters=plot_params,
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
    )


class TestTabularData:
    @pytest.mark.parametrize(
        "x_axis",
        [
            ChartAxisFields.age.name,
            ChartAxisFields.stratum.name,
            ChartAxisFields.metric.name,
        ],
    )
    def test_is_date_based_returns_false_for_non_date_based_x_axis(
        self, x_axis: str, fake_plot_data: PlotGenerationData
    ):
        """
        Given `PlotData` with an `x_axis` parameter which is not `date`
        When the `_is_date_based` property is called
            from an instance of `TabularData`
        Then False is returned
        """
        # Given
        fake_plot_data.parameters.x_axis = x_axis
        tabular_data = TabularData(plots=[fake_plot_data])

        # When
        is_date_based: bool = tabular_data._is_date_based

        # Then
        assert not is_date_based

    def test_is_date_based_returns_true_for_date_based_x_axis(
        self, fake_plot_data: PlotGenerationData
    ):
        """
        Given `PlotData` with an `x_axis` parameter which is set to `date`
        When the `_is_date_based` property is called
            from an instance of `TabularData`
        Then True is returned
        """
        # Given
        fake_plot_data.parameters.x_axis = ChartAxisFields.date.name
        tabular_data = TabularData(plots=[fake_plot_data])

        # When
        is_date_based: bool = tabular_data._is_date_based

        # Then
        assert is_date_based

    def test_cast_combined_plots_in_order_produces_combined_plots_in_order(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given `PlotData` with an `x_axis` parameter which is set to `date`
        When `_cast_combined_plots_in_order()` is called
            from an instance of `TabularData`
        Then the values are reversed and the data is mutated to chronological order
            in descending order.
        """
        # Given
        valid_plot_parameters.x_axis = ChartAxisFields.date.name
        y_axis_values = [1, 2, 4, 5, 5, 2, 1]
        dates_x_axis_values_in_ascending_order = [
            datetime.date(year=2023, month=1, day=i + 1)
            for i in range(len(y_axis_values))
        ]
        original_plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values=dates_x_axis_values_in_ascending_order,
            y_axis_values=y_axis_values,
        )
        tabular_data = TabularData(plots=[original_plot_data])
        plot_data = dict(
            zip(original_plot_data.x_axis_values, original_plot_data.y_axis_values)
        )
        tabular_data.combined_plots = plot_data

        # When
        tabular_data._cast_combined_plots_in_order()

        # Then
        sorted_combined_plots = tabular_data.combined_plots
        assert list(sorted_combined_plots.keys()) == list(
            reversed(original_plot_data.x_axis_values)
        )
        assert list(sorted_combined_plots.values()) == list(
            reversed(original_plot_data.y_axis_values)
        )

    def test_create_tabular_plots_produces_combined_plots_in_order_for_multiple_offset_plots(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given 2 `PlotData` models with an `x_axis` parameter which is set to `date`
            which are offset i.e. 1 plot has more recent data than the other
        When `create_tabular_plots()` is called from an instance of `TabularData`
        Then the data is returned in chronological order, descending from most recent
        """
        # Given
        valid_plot_parameters.x_axis = ChartAxisFields.date.name
        y_axis_values = [1, 2]
        earlier_dates_x_axis_values_in_ascending_order = [
            datetime.date(year=2023, month=1, day=1),
            datetime.date(year=2023, month=1, day=15),
        ]
        earlier_plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values=earlier_dates_x_axis_values_in_ascending_order,
            y_axis_values=y_axis_values,
            additional_values={
                "in_reporting_delay_period": [False for _ in range(len(y_axis_values))]
            },
        )

        y_axis_values = [10, 20, 30, 40]
        later_dates_x_axis_values_in_ascending_order = [
            datetime.date(year=2023, month=1, day=1),
            datetime.date(year=2023, month=1, day=15),
            datetime.date(year=2023, month=8, day=20),
            datetime.date(year=2023, month=8, day=30),
        ]
        later_plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values=later_dates_x_axis_values_in_ascending_order,
            y_axis_values=y_axis_values,
            additional_values={
                "in_reporting_delay_period": [False for _ in range(len(y_axis_values))]
            },
        )
        tabular_data = TabularData(plots=[earlier_plot_data, later_plot_data])

        # When
        tabular_plots = tabular_data.create_tabular_plots()

        # Then
        expected_tabular_plots = [
            {
                "reference": "2023-08-30",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "40",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-08-20",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "30",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-01-15",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "2",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "20",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-01-01",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "1",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "10",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]
        assert tabular_plots == expected_tabular_plots

    def test_create_tabular_plots_produces_combined_plots_in_order_for_multiple_mismatched_plots(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given 2 `PlotData` models with an `x_axis` parameter which is set to `date`
            which are offset i.e. 1 plot has incomplete data
        When `create_tabular_plots()` is called from an instance of `TabularData`
        Then the data is returned in chronological order, descending from most recent
        """
        # Given
        valid_plot_parameters.x_axis = ChartAxisFields.date.name
        y_axis_values = [1, 2]
        missing_dates_x_axis_values_in_ascending_order = [
            datetime.date(year=2023, month=1, day=1),
            datetime.date(year=2023, month=12, day=31),
        ]
        incomplete_plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values=missing_dates_x_axis_values_in_ascending_order,
            y_axis_values=y_axis_values,
        )

        y_axis_values = [10, 20, 30, 40, 50]
        complete_dates_x_axis_values_in_ascending_order = [
            datetime.date(year=2023, month=1, day=1),
            datetime.date(year=2023, month=1, day=15),
            datetime.date(year=2023, month=8, day=20),
            datetime.date(year=2023, month=8, day=30),
            datetime.date(year=2023, month=12, day=31),
        ]
        complete_plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values=complete_dates_x_axis_values_in_ascending_order,
            y_axis_values=y_axis_values,
        )
        tabular_data = TabularData(plots=[incomplete_plot_data, complete_plot_data])

        # When
        tabular_plots = tabular_data.create_tabular_plots()

        # Then
        expected_tabular_plots = [
            {
                "reference": "2023-12-31",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "2",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "50",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-08-30",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "40",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-08-20",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "30",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-01-15",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "20",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-01-01",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "1",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "10",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]
        assert tabular_plots == expected_tabular_plots


class TestAddPlotDataToCombinedPlots:
    def test_basic_behaviour(self, valid_plot_parameters: PlotParameters):
        """
        Given a plot which is not by date
        When `add_plot_data_to_combined_plots()` is called
            from an instance of `TabularData`
        Then the correct response is generated
        """
        # Given
        first_chart_plots_data = dict(zip(["0-4", "5-8"], Y_AXIS_1_VALUES))
        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values="",
            y_axis_values="",
        )

        expected_combined_plots = {
            "0-4": {PLOT_1_LABEL: "10", "in_reporting_delay_period": False},
            "5-8": {PLOT_1_LABEL: "22", "in_reporting_delay_period": False},
        }

        # When
        tabular_data = TabularData(plots=[plot_data])
        tabular_data.add_plot_data_to_combined_plots(
            plot_data=first_chart_plots_data,
            plot_label=PLOT_1_LABEL,
        )

        # Then
        assert tabular_data.combined_plots == expected_combined_plots

    def test_two_plots(self, valid_plot_parameters: PlotParameters):
        """
        Given two plot neither of which are by date
        When `add_plot_data_to_combined_plots()` is called
            from an instance of `TabularData`
        Then the correct response is generated
        """
        first_chart_plots_data = dict(zip(["0-4", "5-8"], Y_AXIS_1_VALUES))
        second_chart_plots_data = dict(zip(["0-4", "5-8"], Y_AXIS_2_VALUES))
        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values="",
            y_axis_values="",
        )

        expected_combined_plots = {
            "0-4": {
                PLOT_1_LABEL: "10",
                PLOT_2_LABEL: "20",
                "in_reporting_delay_period": False,
            },
            "5-8": {
                PLOT_1_LABEL: "22",
                PLOT_2_LABEL: "45",
                "in_reporting_delay_period": False,
            },
        }

        # When
        tabular_data = TabularData(plots=[plot_data])

        tabular_data.add_plot_data_to_combined_plots(
            plot_data=first_chart_plots_data,
            plot_label=PLOT_1_LABEL,
        )
        tabular_data.add_plot_data_to_combined_plots(
            plot_data=second_chart_plots_data,
            plot_label=PLOT_2_LABEL,
        )

        # Then
        assert tabular_data.combined_plots == expected_combined_plots

    def test_add_plot_data_to_combined_plots_includes_confidence_intervals(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given plot data with confidence intervals
        When `add_plot_data_to_combined_plots()` is called
        Then the confidence intervals are included in the result
        """
        # Given
        plot_data = {datetime.date(2023, 1, 1): Decimal("10.5")}
        upper_confidence_lookup = {datetime.date(2023, 1, 1): Decimal("12.0")}
        lower_confidence_lookup = {datetime.date(2023, 1, 1): Decimal("9.0")}

        tabular_data = TabularData(
            plots=[
                PlotGenerationData(
                    parameters=valid_plot_parameters,
                    x_axis_values="",
                    y_axis_values="",
                )
            ]
        )

        # When
        tabular_data.add_plot_data_to_combined_plots(
            plot_data=plot_data,
            plot_label=PLOT_1_LABEL,
            upper_confidence_lookup=upper_confidence_lookup,
            lower_confidence_lookup=lower_confidence_lookup,
        )

        # Then
        assert tabular_data.combined_plots["2023-01-01"][UPPER_CONFIDENCE] == "12.0"
        assert tabular_data.combined_plots["2023-01-01"][LOWER_CONFIDENCE] == "9.0"


class TestCombineAllPlots:
    def test_plot_with_sequential_date_point(self):
        """
        Given a `TabularPlotData` model with x-axis values for consecutive dates
        When `combine_all_plots()` is called
        Then the correct response is generated
        """
        # Given
        x_axis_values = [
            datetime.date(2023, 9, 1),
            datetime.date(2023, 9, 2),
            datetime.date(2023, 9, 3),
            datetime.date(2023, 9, 4),
        ]
        first_chart_plots_data = _create_plot_data(
            x_axis_values=x_axis_values,
            y_axis_values=[10, 66, 22, 26],
            label=PLOT_1_LABEL,
        )

        # When
        tabular_data = TabularData(plots=[first_chart_plots_data])
        tabular_data.combine_all_plots()

        # Then
        # Check plot labels are as expected
        assert len(tabular_data.plot_labels) == 1
        assert tabular_data.plot_labels[0] == PLOT_1_LABEL

        # Check combined plot output is as expected
        combined_plots = tabular_data.combined_plots
        assert combined_plots["2023-09-01"] == {
            PLOT_1_LABEL: str(10),
            "in_reporting_delay_period": False,
        }
        assert combined_plots["2023-09-02"] == {
            PLOT_1_LABEL: str(66),
            "in_reporting_delay_period": False,
        }
        assert combined_plots["2023-09-03"] == {
            PLOT_1_LABEL: str(22),
            "in_reporting_delay_period": False,
        }
        assert combined_plots["2023-09-04"] == {
            PLOT_1_LABEL: str(26),
            "in_reporting_delay_period": False,
        }


class TestCreateMultiPlotOutput:
    def test_2_plots(self, valid_plot_parameters: PlotParameters):
        """
        Given 2 plots with plot labels
        When `create_multi_plot_output()` is called
            from an instance of `TabularData`
        Then the correct response is generated
        """
        # Given
        plot_labels = ["Plot1", "Plot2"]
        combined_plots = {
            "2022-09-19": {"Plot1": "22", "Plot2": "33"},
            "2022-09-06": {"Plot1": "06", "Plot2": "63"},
            "2022-09-05": {"Plot1": "10", "Plot2": "11"},
        }

        expected_output = [
            {
                "date": "2022-09-19",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "22",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "33",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "date": "2022-09-06",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "06",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "63",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "date": "2022-09-05",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "10",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "11",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]
        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values="",
            y_axis_values="",
        )

        # When
        tabular_data = TabularData(plots=[plot_data])
        tabular_data.plot_labels = plot_labels
        tabular_data.combined_plots = combined_plots
        tabular_data.column_heading = "date"
        actual_output = tabular_data.create_multi_plot_output()

        # Then
        assert actual_output == expected_output

    def test_plots_of_unequal_length(self, valid_plot_parameters: PlotParameters):
        """
        Given 2 plots which are not the same length as each other
        When `create_multi_plot_output()` is called
            from an instance of `TabularData`
        Then the correct response is generated
        """
        # Given
        plot_labels = ["Plot1", "Plot2"]
        combined_plots = {
            "2022-09-25": {"Plot2": "44"},
            "2022-09-19": {"Plot1": "22", "Plot2": "33"},
            "2022-09-06": {"Plot2": "06"},
            "2022-09-05": {"Plot1": "10"},
        }
        expected_output = [
            {
                "date": "2022-09-25",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "44",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "date": "2022-09-19",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "22",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "33",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "date": "2022-09-06",
                "values": [
                    {
                        "label": "Plot1",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": "06",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "date": "2022-09-05",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "10",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Plot2",
                        "value": None,
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]
        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values="",
            y_axis_values="",
        )

        # When
        tabular_data = TabularData(plots=[plot_data])
        tabular_data.plot_labels = plot_labels
        tabular_data.combined_plots = combined_plots
        tabular_data.column_heading = "date"
        actual_output = tabular_data.create_multi_plot_output()

        # Then
        assert actual_output == expected_output

    def test_plots_for_headline_data(
        self, valid_plot_parameters_for_headline_data: PlotParameters
    ):
        """
        Given a series of plots for a headline data chart
        When `create_multi_plot_output()` is called
        Then the correct output is returned.
        """
        # Given
        plot_labels = ["01 - 04", "05 - 10", "11 - 14"]
        combined_plots = {
            "01 - 04": {"01 - 04": "55"},
            "05 - 10": {"05 - 10": "65"},
            "11 - 14": {"11 - 14": "75"},
        }
        expected_output = [
            {
                "reference": "01 - 04",
                "values": [
                    {
                        "label": "Amount",
                        "value": "55",
                        "in_reporting_delay_period": False,
                    }
                ],
            },
            {
                "reference": "05 - 10",
                "values": [
                    {
                        "label": "Amount",
                        "value": "65",
                        "in_reporting_delay_period": False,
                    }
                ],
            },
            {
                "reference": "11 - 14",
                "values": [
                    {
                        "label": "Amount",
                        "value": "75",
                        "in_reporting_delay_period": False,
                    }
                ],
            },
        ]
        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters_for_headline_data,
            x_axis_values="",
            y_axis_values="",
        )

        # When
        tabular_data = TabularData(plots=[plot_data])
        tabular_data.plot_labels = plot_labels
        tabular_data.combined_plots = combined_plots
        actual_output = tabular_data.create_multi_plot_output()

        # Then
        assert actual_output == expected_output

    def test_create_timeseries_plot_values_includes_confidence_intervals(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given plot values with confidence intervals
        When `create_timeseries_plot_values()` is called
        Then the confidence intervals are included in the result
        """
        # Given
        plot_values = {
            PLOT_1_LABEL: "10.5",
            "in_reporting_delay_period": False,
            UPPER_CONFIDENCE: "12.0",
            LOWER_CONFIDENCE: "9.0",
        }

        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters,
            x_axis_values="",
            y_axis_values="",
        )
        tabular_data = TabularData(plots=[plot_data])
        tabular_data.plot_labels = [PLOT_1_LABEL]

        # When
        result = tabular_data.create_timeseries_plot_values(plot_values=plot_values)

        # Then
        assert len(result) == 1
        assert result[0][UPPER_CONFIDENCE] == "12.0"
        assert result[0][LOWER_CONFIDENCE] == "9.0"

    def test_create_headline_plot_values_includes_confidence_intervals(
        self, valid_plot_parameters_for_headline_data: PlotParameters
    ):
        """
        Given headline plot values with confidence intervals
        When `create_headline_plot_values()` is called
        Then the confidence intervals are included in the result
        """
        # Given
        plot_values = {
            "01 - 04": "55.0",
            UPPER_CONFIDENCE: "60.0",
            LOWER_CONFIDENCE: "50.0",
        }

        plot_data = PlotGenerationData(
            parameters=valid_plot_parameters_for_headline_data,
            x_axis_values="",
            y_axis_values="",
        )
        tabular_data = TabularData(plots=[plot_data])
        tabular_data.plot_labels = ["01 - 04"]

        # When
        result = tabular_data.create_headline_plot_values(plot_values=plot_values)

        # Then
        assert len(result) == 1
        assert result[0][UPPER_CONFIDENCE] == "60.0"
        assert result[0][LOWER_CONFIDENCE] == "50.0"
