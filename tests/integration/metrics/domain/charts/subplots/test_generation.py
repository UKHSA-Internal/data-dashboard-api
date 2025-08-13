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
            target_threshold=95,
            target_threshold_label="95% target",
        )

    def test_chart_figure_returns_correctly_with_threshold(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
    ):
        """
        Given a valid payload for a `Subplot Chart`
            which does specify a `target_threshold`
        When the `generate_chart_figure` method is called
        Then a valid plotly `Figure` object is returned
            with the threshold bar rendered
        """
        # Given
        valid_payload: SubplotChartGenerationPayload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=valid_payload
        )

        # Then
        assert len(figure.data) == 5
        assert "Darlington" in figure.data[0].x
        assert "Hartlepool" in figure.data[1].x
        assert "Darlington" in figure.data[2].x
        assert "Hartlepool" in figure.data[3].x

        threshold_bar = figure.data[4]
        assert threshold_bar.name == "95% target"

    def test_chart_figure_renders_correctly_without_threshold(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
    ):
        """
        Given a valid payload for a `Subplot Chart`
            which does not specify a `target_threshold`
        When the `generate_chart_figure` method is called
        Then a valid plotly `Figure` object is returned
            without the threshold bar rendered
        """
        # Given
        valid_payload: SubplotChartGenerationPayload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )
        valid_payload.target_threshold = None

        # When
        figure: plotly.graph_objects.Figure = generate_chart_figure(
            chart_generation_payload=valid_payload
        )

        # Then
        assert len(figure.data) == 4
        assert "Darlington" in figure.data[0].x
        assert "Hartlepool" in figure.data[1].x
        assert "Darlington" in figure.data[2].x
        assert "Hartlepool" in figure.data[3].x
