from unittest import mock
import pytest

from metrics.interfaces.charts.common import generation

MODULE_PATH = "metrics.interfaces.charts.common.generation"


class TestGenerateEncodedChart:
    @mock.patch(f"{MODULE_PATH}._create_optimized_svg")
    def test_delegates_call_for_validation(
        self,
        mocked_create_optimized_svg: mock.MagicMock,
    ):
        """
        Given mocked chart request parameters and a charts interface class
        When `generate_encoded_chart()` is called
        Then a call is delegated to `generate_chart_figure`
            from an instance of the interface class
        And the enriched `ChartResult` model
            contains the expected deliverables

        Patches:
            `mocked_create_optimized_svg`: To remove the side effect
                of having to encode the chart figure

        """
        # Given
        spy_chart_request_params = mock.Mock(file_format="svg")
        spy_interface_class = mock.Mock()
        mocked_create_optimized_svg.return_value = "abc"

        # When
        chart_result: generation.ChartResult = generation.generate_encoded_chart(
            chart_request_params=spy_chart_request_params, interface=spy_interface_class
        )

        # Then
        spy_interface_class.assert_called_once_with(
            chart_request_params=spy_chart_request_params
        )

        chart_output = (
            spy_interface_class.return_value.generate_chart_output.return_value
        )
        assert chart_result.last_updated == spy_interface_class.last_updated
        assert chart_result.alt_text == chart_output.alt_text
        assert chart_result.figure == chart_output.interactive_chart_figure_output
        assert chart_result.chart == mocked_create_optimized_svg.return_value


class TestEncodeFigure:
    @pytest.mark.parametrize(
        "file_format",
        [
            "png",
            "jpg",
            "jpeg",
        ],
    )
    def test_invalid_file_format_raises_error(self, file_format: str):
        """
        Given the user supplies an invalid `file_format`
        When `_encode_figure` is called
        Then an `InvalidFileFormatError` is raised
        """
        # Given
        mocked_figure = mock.Mock()

        # When / Then
        with pytest.raises(ValueError):
            generation._encode_figure(figure=mocked_figure, file_format=file_format)

    @mock.patch(f"{MODULE_PATH}.urllib.parse.quote_plus")
    @mock.patch(f"{MODULE_PATH}._create_optimized_svg")
    def test_calls_are_delegated_successfully_to_render_optimised_svg(
        self,
        spy_create_optimized_svg: mock.MagicMock,
        spy_urllib_quote_plus: mock.MagicMock,
    ):
        """
        Given a mocked plotly figure and `file_format` of svg
        When `_encode_figure()` is called
        Then the call is delegated to
            `_create_optimized_svg`
            and then to `quote_plus()` from `urllib`
        """
        # Given
        file_format = "svg"
        mocked_figure = mock.Mock()
        spy_create_optimized_svg.return_value = "abc"

        # When
        encoded_figure = generation._encode_figure(
            figure=mocked_figure, file_format=file_format
        )

        # Then
        spy_create_optimized_svg.assert_called_once_with(
            figure=mocked_figure, file_format=file_format
        )
        spy_urllib_quote_plus.assert_called_once_with(
            spy_create_optimized_svg.return_value
        )
        assert encoded_figure == spy_urllib_quote_plus.return_value


class TestGenerateChartAsFile:
    @mock.patch(f"{MODULE_PATH}._write_figure")
    def test_delegates_call_for_writing_chart(
        self,
        spy_write_figure: mock.MagicMock,
    ):
        """
        Given mocked chart request parameters and a charts interface class
        When `generate_chart_as_file()` is called
        Then a call is delegated to `generate_chart_figure`
            from an instance of the interface class
        And call is delegated to `_write_figure()`
            to produce the chart
        """
        # Given
        spy_chart_request_params = mock.Mock(file_format="png")
        spy_interface_class = mock.Mock()

        # When
        generated_chart = generation.generate_chart_as_file(
            chart_request_params=spy_chart_request_params, interface=spy_interface_class
        )

        # Then
        spy_interface_class.assert_called_once_with(
            chart_request_params=spy_chart_request_params
        )
        chart_output = (
            spy_interface_class.return_value.generate_chart_output.return_value
        )
        spy_write_figure.assert_called_once_with(
            figure=chart_output.figure,
            file_format=spy_chart_request_params.file_format,
        )

        assert generated_chart == spy_write_figure.return_value
