from unittest import mock

import pytest

from metrics.domain.charts.common_charts.plots.line_multi_coloured import properties


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
    def test_get_chart_line_type_defaults_to_solid(self, invalid_line_type: str | None):
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
