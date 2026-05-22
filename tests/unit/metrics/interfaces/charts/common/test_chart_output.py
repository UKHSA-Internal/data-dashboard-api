from unittest import mock
import pytest

import plotly.graph_objects as go


from metrics.interfaces.charts.common.chart_output import ChartOutput, wrap_text

MODULE_PATH = "metrics.interfaces.charts.common.chart_output"

WATERMARK_FONT_SIZE = 40
WATERMARK_FONT_COLOUR = "rgba(0, 0, 0, 0.25)"
WATERMARK_OPACITY = 0.58


class TestWrapText:
    def test_wraps_text_into_br_separated_lines(self):
        """
        Given a string longer than max_chars_per_line
        When wrap_text() is called
        Then the text is wrapped and joined with <br>
        """
        # Given
        text = "This is a long string that should be wrapped properly"
        max_chars = 10

        # When
        result = wrap_text(text, max_chars_per_line=max_chars)

        # Then
        expected = "<br>".join(
            [
                "This is a",
                "long",
                "string",
                "that",
                "should be",
                "wrapped",
                "properly",
            ]
        )
        assert result == expected

    def test_returns_single_line_when_text_is_short(self):
        """
        Given a string shorter than max_chars_per_line
        When wrap_text() is called
        Then the original text is returned without <br>
        """
        # Given
        text = "Short text"

        # When
        result = wrap_text(text, max_chars_per_line=20)

        # Then
        assert result == text

    def test_handles_empty_string(self):
        """
        Given an empty string
        When wrap_text() is called
        Then an empty string is returned
        """
        # Given
        text = ""

        # When
        result = wrap_text(text, max_chars_per_line=10)

        # Then
        assert result == ""

    from unittest import mock


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
    @mock.patch(f"{MODULE_PATH}.wrap_text")
    @mock.patch(f"{MODULE_PATH}.DataClassification")
    @mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True)
    def test_adds_wrapped_watermark_annotation(
        self, mock_data_classification, mock_wrap_text
    ):
        """
        Given a ChartOutput with a valid data_classification
        When _apply_watermark() is called
        Then the watermark text is resolved, wrapped, and added as an annotation
        """
        # Given / When (apply is called with postInit on instantiation)
        figure = mock.Mock(spec=go.Figure)

        mock_data_classification.__getitem__.return_value.value = "Highly Confidential"
        mock_wrap_text.return_value = "Highly<br>Confidential"

        ChartOutput(
            figure=figure,
            description="Test",
            is_headline=False,
            is_public=False,
            data_classification="official",
        )

        # Then
        mock_data_classification.__getitem__.assert_called_once_with("official")
        mock_wrap_text.assert_called_once_with("Highly Confidential", 16)

        figure.add_annotation.assert_called_once_with(
            text="Highly<br>Confidential",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={
                "size": WATERMARK_FONT_SIZE,
                "color": WATERMARK_FONT_COLOUR,
            },
            textangle=-30,
            opacity=WATERMARK_OPACITY,
        )
