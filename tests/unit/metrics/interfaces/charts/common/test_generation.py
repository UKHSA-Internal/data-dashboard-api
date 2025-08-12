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


class TestChartResult:
    def test_output(self):
        """
        Given an enriched `ChartResult` model
        When `output() is called
        Then a dict representation of
            the `ChartResult` is returned
        """
        # Given
        last_updated = "2025-01-01"
        chart = "abc"
        alt_text = "def"
        figure = {"figure": "hij"}

        chart_result = generation.ChartResult(
            last_updated=last_updated,
            chart=chart,
            alt_text=alt_text,
            figure=figure,
        )

        # When
        output: dict = chart_result.output()

        # Then
        assert output["last_updated"] == last_updated
        assert output["chart"] == chart
        assert output["alt_text"] == alt_text
        assert output["figure"] == figure


class TestCreateOptimizedSVG:
    @mock.patch(f"{MODULE_PATH}.scour.scourString")
    def test_delegates_calls_successfully(self, spy_scour_string: mock.Mock):
        """
        Given a mocked plotly figure and `file_format` of svg
        When `_create_optimized_svg()` is called
        Then the figure is created
            and passed to the `scourString()` call
        """
        # Given
        spy_figure = mock.Mock()
        file_format = "svg"

        # When
        optimized_svg: str = generation._create_optimized_svg(
            figure=spy_figure, file_format=file_format
        )

        # Then
        spy_figure.to_image.assert_called_once_with(format=file_format, validate=False)
        svg_image = spy_figure.to_image.return_value
        spy_scour_string.assert_called_once_with(in_string=svg_image)

        assert optimized_svg == spy_scour_string.return_value


class TestWriteFigure:
    @mock.patch(f"{MODULE_PATH}.io.BytesIO")
    def test_creates_image(self, spy_bytes_io_class: mock.MagicMock):
        """
        Given a mocked plotly figure and `file_format` of png
        When `_write_figure()` is called
        Then `write_image()` is called from the figure object
        And returned in a bytes IO stream
        """
        # Given
        mocked_figure = mock.Mock()
        file_format = "png"

        # When
        written_figure = generation._write_figure(
            figure=mocked_figure, file_format=file_format
        )

        # Then
        mocked_figure.write_image.assert_called_once_with(
            file=spy_bytes_io_class.return_value,
            format=file_format,
            validate=False,
        )
        bytes_io = spy_bytes_io_class.return_value
        bytes_io.seek.assert_called_once_with(0)
        assert written_figure == bytes_io.getvalue.return_value
