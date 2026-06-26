from unittest import mock
import pytest

import plotly.graph_objects as go


from metrics.domain.common.utils import DEFAULT_CHART_WIDTH
from metrics.interfaces.charts.common.chart_output import ChartOutput

MODULE_PATH = "metrics.interfaces.charts.common.chart_output"

WATERMARK_FONT_COLOUR = "rgba(0, 0, 0, 0.25)"
WATERMARK_OPACITY = 0.58


class TestPostInitAppliesWatermark:
    @mock.patch(f"{MODULE_PATH}.ChartOutput._apply_watermark")
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True)
    def test_applies_watermark_when_not_public_and_classified_and_auth_enabled(
        self, spy_apply_watermark: mock.MagicMock
    ):
        """
        Given an instance that is not public and has data_classification
        When __post_init__() is triggered
        Then _apply_watermark() is called
        """
        # Given / When
        ChartOutput(
            figure=go.Figure(),
            description="Test chart",
            is_headline=False,
            is_public=False,
            data_classification="official",
        )

        # Then
        spy_apply_watermark.assert_called_once()

    @mock.patch(f"{MODULE_PATH}.ChartOutput._apply_watermark")
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True)
    def test_does_not_apply_watermark_when_public(
        self, spy_apply_watermark: mock.MagicMock
    ):
        """
        Given an instance that is public
        When __post_init__() is triggered
        Then _apply_watermark() is not called
        """
        # Given / When
        ChartOutput(
            figure=go.Figure(),
            description="Test chart",
            is_headline=False,
            data_classification="official",
        )

        # Then
        spy_apply_watermark.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.ChartOutput._apply_watermark")
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True)
    def test_does_not_apply_watermark_when_no_classification(
        self, spy_apply_watermark: mock.MagicMock
    ):
        """
        Given an instance that has no data_classification
        When __post_init__() is triggered
        Then _apply_watermark() is not called
        """
        # Given / When
        ChartOutput(
            figure=go.Figure(),
            description="Test chart",
            is_headline=False,
        )

        # Then
        spy_apply_watermark.assert_not_called()

    @mock.patch(f"{MODULE_PATH}.ChartOutput._apply_watermark")
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", False)
    def test_does_not_apply_watermark_when_no_auth_enabled(
        self, spy_apply_watermark: mock.MagicMock
    ):
        """
        Given an instance that has no data_classification
        When __post_init__() is triggered
        Then _apply_watermark() is not called
        """
        # Given / When
        ChartOutput(
            figure=go.Figure(),
            description="Test chart",
            is_headline=False,
            is_public=False,
            data_classification="official",
        )

        # Then
        spy_apply_watermark.assert_not_called()


class TestApplyWatermark:
    @mock.patch(f"{MODULE_PATH}.DataClassification")
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True)
    def test_adds_watermark_annotation(self, mock_data_classification):
        """
        Given a ChartOutput with a valid data_classification
        When _apply_watermark() is called
        Then the watermark text is resolved, and added as a scaled annotation
        """
        # Given / When (apply is called with postInit on instantiation)
        figure = mock.Mock(spec=go.Figure)

        # mock layout.width for scaling logic
        font_size = (DEFAULT_CHART_WIDTH * 0.75) / (
            max(len("Highly Confidential"), 1) * 0.6
        )
        expected_font_size = round(max(8, min(font_size, 300)))

        mock_data_classification.__getitem__.return_value.value = "Highly Confidential"

        ChartOutput(
            figure=figure,
            description="Test",
            is_headline=False,
            is_public=False,
            data_classification="official",
        )

        # Then
        mock_data_classification.__getitem__.assert_called_once_with("official")

        figure.add_annotation.assert_called_once_with(
            text="Highly Confidential",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.8,
            showarrow=False,
            font={
                "size": expected_font_size,
                "color": WATERMARK_FONT_COLOUR,
            },
            textangle=0,
            opacity=WATERMARK_OPACITY,
        )
