from decimal import Decimal
import datetime
from typing import Any
from unittest import mock

import plotly.graph_objects
from plotly.subplots import make_subplots

from metrics.domain.charts.subplots.generation import generate_chart_figure
from metrics.domain.models import PlotGenerationData, PlotParameters
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload


class TestSubplotGeneration:
    @staticmethod
    def _setup_chart_plot_data(
        example_subplot_chart_generation_payload: SubplotChartGenerationPayload,
    ) -> SubplotChartGenerationPayload:
        return SubplotChartGenerationPayload(
            subplot_data=example_subplot_chart_generation_payload,
            chart_width=500,
            chart_height=900,
            y_axis_title="y-axis-title",
            x_axis_title="x-axis-title",
            y_axis_maximum_value=None,
            y_axis_minimum_value=0,
            target_threshold=0.95,
        )

    def test_chart_figure_returns_correctly(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
    ):
        """
        Given a valid payload for a `Subplot Chart`
        When the `generate_chart_figure` method is called
        Then a valid plotly `Figure` object is returned.
        """
        # Given
        valid_payload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )

        # When
        chart_image = generate_chart_figure(chart_generation_payload=valid_payload)

        # Then
        assert len(chart_image.data) == 4
        assert "Darlington" in chart_image.data[0].x
        assert "Hartlepool" in chart_image.data[1].x
        assert "Darlington" in chart_image.data[2].x
        assert "Hartlepool" in chart_image.data[3].x
