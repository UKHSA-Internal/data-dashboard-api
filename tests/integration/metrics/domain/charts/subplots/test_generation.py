import math

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
        assert len(chart_image.data) == 6
        assert "Darlington" in chart_image.data[0].x
        assert "Hartlepool" in chart_image.data[1].x
        assert "Stockton-on-Tees" in chart_image.data[2].x
        assert "Darlington" in chart_image.data[3].x
        assert "Hartlepool" in chart_image.data[4].x
        assert "Stockton-on-Tees" in chart_image.data[5].x

    def test_chart_figure_includes_one_tick_text_for_each_subplot(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
    ):
        """
        Given a valid payload for a `Subplot Chart`
        When the `generate_chart_figure` method is called
        Then: The generated Figure contains ticktext that matches the subplot_title
        """
        # Given
        valid_payload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )

        # When
        chart_image = generate_chart_figure(chart_generation_payload=valid_payload)

        # Then
        assert (
            valid_payload.subplot_data[0].subplot_title
            in chart_image.layout.xaxis.ticktext
        )
        assert (
            valid_payload.subplot_data[1].subplot_title
            in chart_image.layout.xaxis2.ticktext
        )

    def test_chart_figure_x_axis_tick_value_in_correct_play(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
    ):
        """
        Given: A valid payload for a `Subplot Chart`
        When: The generate_chart_figure method is called
        Then: Each subplot in the generated Figure contains exactly one tickval
            positioned at the center index of that subplot

            Example: For a list of 3 subplots [0, 1, 2], the tick should be at index 1
        """
        # Given
        valid_payload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )

        # When
        chart_image = generate_chart_figure(chart_generation_payload=valid_payload)
        expected_xaxis_tickval = (
            math.ceil(len(valid_payload.subplot_data[0].subplot_data) / 2) - 1
        )
        expected_xaxis2_tickval = (
            math.ceil(len(valid_payload.subplot_data[1].subplot_data) / 2) - 1
        )

        # Then
        assert len(chart_image.layout.xaxis.tickvals) == 1
        assert expected_xaxis_tickval in chart_image.layout.xaxis.tickvals
        assert len(chart_image.layout.xaxis2.tickvals) == 1
        assert expected_xaxis2_tickval in chart_image.layout.xaxis2.tickvals
