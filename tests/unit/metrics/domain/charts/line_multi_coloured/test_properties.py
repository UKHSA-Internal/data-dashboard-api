from typing import Optional
from unittest import mock

import pytest

from metrics.domain.charts.line_multi_coloured import properties


class TestChartLineTypes:
    @pytest.mark.parametrize("chart_line_type_enum", properties.ChartLineTypes)
    def test_get_chart_line_type(self, chart_line_type_enum: properties.ChartLineTypes):
        """
        Given a valid chart line type string e.g. "SOLID"
        When `get_chart_line_type()` is called from the `ChartLineTypes` class
        Then the correct enum is returned
        """
        # Given
        chart_line_type: str = chart_line_type_enum.name

        # When
        retrieved_chart_line_type: properties.ChartLineTypes = (
            properties.ChartLineTypes.get_chart_line_type(line_type=chart_line_type)
        )

        # Then
        assert type(retrieved_chart_line_type) is properties.ChartLineTypes
        assert retrieved_chart_line_type.name == chart_line_type

    @pytest.mark.parametrize(
        "invalid_line_type", [(None, "null", "", "NON-EXISTENT-LINE-TYPE", "HOLLOW")]
    )
    def test_get_chart_line_type_defaults_to_solid(
        self, invalid_line_type: Optional[str]
    ):
        """
        Given an invalid chart line type string
        When `get_chart_line_type()` is called from the `ChartLineTypes` class
        Then the `SOLID` enum is defaulted to and returned
        """
        # Given
        line_type: str = invalid_line_type

        # When
        retrieved_line_type = properties.ChartLineTypes.get_chart_line_type(
            line_type=line_type
        )

        # Then
        assert type(retrieved_line_type) is properties.ChartLineTypes
        assert retrieved_line_type == properties.ChartLineTypes.SOLID


class TestIsLegendRequired:
    @staticmethod
    def _mocked_chart_plot_data_without_label() -> mock.Mock:
        mocked_parameters_without_label = mock.Mock(label="")
        return mock.Mock(parameters=mocked_parameters_without_label)

    @staticmethod
    def _mocked_chart_plot_data_with_label() -> mock.Mock:
        mocked_parameters_without_label = mock.Mock(label="some_label")
        return mock.Mock(parameters=mocked_parameters_without_label)

    def test_returns_true_if_all_chart_plots_data_params_contain_label(self):
        """
        Given a list of mocked chart plot data objects which all contain a `label`
        When `is_legend_required()` is called
        Then True is returned
        """
        # Given
        chart_plots_data = [self._mocked_chart_plot_data_with_label()] * 2

        # When
        legend_is_required: bool = properties.is_legend_required(
            chart_plots_data=chart_plots_data
        )

        # Then
        assert legend_is_required

    def test_returns_true_if_at_least_one_chart_plots_data_params_contain_label(self):
        """
        Given a list of mocked chart plot data objects of which 1 contains a `label`
        When `is_legend_required()` is called
        Then True is returned
        """
        # Given
        chart_plots_data = [
            self._mocked_chart_plot_data_with_label(),
            self._mocked_chart_plot_data_without_label(),
        ]

        # When
        legend_is_required: bool = properties.is_legend_required(
            chart_plots_data=chart_plots_data
        )

        # Then
        assert legend_is_required

    def test_returns_false_if_no_chart_plots_data_params_contain_label(self):
        """
        Given a list of mocked chart plot data objects, none of which contain a `label`
        When `is_legend_required()` is called
        Then False is returned
        """
        # Given
        chart_plots_data = [self._mocked_chart_plot_data_without_label()] * 2

        # When
        legend_is_required: bool = properties.is_legend_required(
            chart_plots_data=chart_plots_data
        )

        # Then
        assert not legend_is_required
