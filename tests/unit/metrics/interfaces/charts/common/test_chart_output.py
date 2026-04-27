import plotly.graph_objects as go
import pytest

from metrics.interfaces.charts.common.chart_output import (
    CHART_BG_COLOUR,
    ChartOutput,
    DEFAULT_DATA_CLASSIFICATION,
    WATERMARK_FONT_COLOUR,
    WATERMARK_FONT_SIZE,
    WATERMARK_OPACITY,
)


def _make_figure() -> go.Figure:
    """
    A minimal Plotly figure without any watermark annotation
    """

    return go.Figure()


class TestChartOutputWatermark:
    def test_no_watermark_when_is_public_true(self):
        """
        Given `is_public=True` (the default)
        When a `ChartOutput` instance is created
        Then no watermark annotation is added to the figure
        """

        # Given / When
        figure = _make_figure()
        chart_output = ChartOutput(
            figure=figure,
            description="test",
            is_headline=False,
            is_public=True,
        )

        # Then
        assert len(chart_output.figure.layout.annotations) == 0

    def test_watermark_added_when_is_public_false(self):
        """
        Given `is_public=False`
        When a `ChartOutput` instance is created
        Then a watermark annotation is added to the figure
        """

        # Given / When
        figure = _make_figure()
        chart_output = ChartOutput(
            figure=figure,
            description="test",
            is_headline=False,
            is_public=False,
        )

        # Then
        assert len(chart_output.figure.layout.annotations) == 1

    def test_watermark_uses_default_classification_when_none_provided(self):
        """
        Given `is_public=False` and no `data_classification` provided
        When a `ChartOutput` instance is created
        Then the watermark text is the DEFAULT_DATA_CLASSIFICATION value
        """

        # Given / When
        figure = _make_figure()
        chart_output = ChartOutput(
            figure=figure,
            description="test",
            is_headline=False,
            is_public=False,
            data_classification=None,
        )

        # Then
        annotation = chart_output.figure.layout.annotations[0]
        assert annotation.text == DEFAULT_DATA_CLASSIFICATION

    def test_watermark_annotation_is_centred_in_paper_coordinates(self):
        """
        Given `is_public=False`
        When a `ChartOutput` instance is created
        Then the watermark annotation uses paper coordinates
            and is positioned at the centre of the chart
        """

        # Given / When
        figure = _make_figure()
        chart_output = ChartOutput(
            figure=figure,
            description="test",
            is_headline=False,
            is_public=False,
        )

        # Then
        annotation = chart_output.figure.layout.annotations[0]
        assert annotation.xref == "paper"
        assert annotation.yref == "paper"
        assert annotation.x == 0.5
        assert annotation.y == 0.5
        assert annotation.showarrow is False

    def test_watermark_annotation_is_diagonal(self):
        """
        Given `is_public=False`
        When a `ChartOutput` instance is created
        Then the watermark annotation has a negative rotation
            so it displays diagonally
        """

        # Given / When
        figure = _make_figure()
        chart_output = ChartOutput(
            figure=figure,
            description="test",
            is_headline=False,
            is_public=False,
        )

        # Then
        annotation = chart_output.figure.layout.annotations[0]
        assert annotation.textangle == -30
