import pytest
import math

from decimal import Decimal

import plotly.graph_objects

from metrics.domain.charts.subplots.generation import generate_chart_figure
from metrics.domain.models.subplot_plots import SubplotChartGenerationPayload

from metrics.domain.charts.chart_settings.subplot_chart_settings import (
    DEFAULT_CHART_BASE_Y,
    DEFAULT_CHART_MULTIPLIER,
    THIRD_CHART_WIDTH,
    THIRD_CHART_BASE_Y,
    THIRD_CHART_MULTIPLIER,
    NARROW_CHART_WIDTH,
    NARROW_CHART_BASE_Y,
    NARROW_CHART_MULTIPLIER,
    HALF_CHART_WIDTH,
    HALF_CHART_BASE_Y,
    HALF_CHART_MULTIPLIER,
    WIDE_CHART_WIDTH,
    WIDE_CHART_BASE_Y,
    WIDE_CHART_MULTIPLIER,
)


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
        assert len(figure.data) == 6
        assert "Darlington" in figure.data[0].x
        assert "Hartlepool" in figure.data[1].x
        assert "Stockton-on-Tees" in figure.data[2].x
        assert "Darlington" in figure.data[3].x
        assert "Hartlepool" in figure.data[4].x
        assert "Stockton-on-Tees" in figure.data[5].x

        x_axis_annotation = figure.layout.annotations[0]
        assert x_axis_annotation.text == valid_payload.x_axis_title

        target_threshold_annotation = figure.layout.annotations[1]
        assert target_threshold_annotation.text == valid_payload.target_threshold_label

    def test_chart_figure_includes_one_tick_text_for_each_subplot(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
    ):
        """
        Given a valid payload for a `Subplot Chart`
        When the `generate_chart_figure` method is called
        Then the generated Figure contains
            ticktext that matches the subplot_title
        """
        # Given
        valid_payload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )

        # When
        chart_image = generate_chart_figure(chart_generation_payload=valid_payload)

        # Then
        assert len(chart_image.layout.xaxis.ticktext) == 1
        assert len(chart_image.layout.xaxis2.ticktext) == 1

    @pytest.mark.parametrize(
        "subplot_title, formatted_subplot_title",
        (
            ("6-in-1", "<b>6-in-1</b>"),
            ("6-in-1 (24m)", "<b>6-in-1</b><br>(24m)"),
            ("MVC Boost (24m)", "<b>MVC Boost</b><br>(24m)"),
        ),
    )
    def test_chart_figure_formats_tick_text_correctly(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
        subplot_title: str,
        formatted_subplot_title: str,
    ):
        """
        Given a valid payload for a `Subplot Chart`
        When the `generate_chart_figure` method is called
        Then each subplot's ticktext will include correct formatting.
        """
        # Given
        valid_payload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )
        valid_payload.subplot_data[0].subplot_title = subplot_title

        # When
        chart_image = generate_chart_figure(chart_generation_payload=valid_payload)
        expected_subplot_title = formatted_subplot_title

        # Then
        assert expected_subplot_title in chart_image.layout.xaxis.ticktext

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

    @pytest.mark.parametrize(
        "chart_width, y_base, y_multiplier",
        (
            (THIRD_CHART_WIDTH, THIRD_CHART_BASE_Y, THIRD_CHART_MULTIPLIER),
            (NARROW_CHART_WIDTH, NARROW_CHART_BASE_Y, NARROW_CHART_MULTIPLIER),
            (HALF_CHART_WIDTH, HALF_CHART_BASE_Y, HALF_CHART_MULTIPLIER),
            (WIDE_CHART_WIDTH, WIDE_CHART_BASE_Y, WIDE_CHART_MULTIPLIER),
            (1101, DEFAULT_CHART_BASE_Y, DEFAULT_CHART_MULTIPLIER),
        ),
    )
    def test_chart_renders_correct_legend_y_post_based_on_chart_width(
        self,
        example_subplot_chart_generation_payload: list[dict[str, str | Decimal]],
        chart_width: int,
        y_base: int,
        y_multiplier: int,
    ):
        """
        Given a valid payload for a `Subplot Chart`
        When the `generate_chart_figure` method is called
        Then the plotly `Figure` object's legend position is correct
            based on the chart width request.
        """
        # Given
        valid_payload = self._setup_chart_plot_data(
            example_subplot_chart_generation_payload=example_subplot_chart_generation_payload,
        )
        valid_payload.chart_width = chart_width

        # When
        chart_image = generate_chart_figure(chart_generation_payload=valid_payload)
        expected_y_position = -(y_base * y_multiplier)

        # Then
        assert expected_y_position == chart_image.layout.legend.y
