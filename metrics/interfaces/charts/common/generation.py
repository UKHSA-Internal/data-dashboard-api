import datetime
import io
import urllib
from dataclasses import asdict, dataclass

import plotly
from scour import scour


@dataclass
class ChartResult:
    last_updated: str | datetime.date
    chart: str
    alt_text: str
    figure: dict

    def output(self) -> dict:
        return asdict(self)


def generate_encoded_chart(
    *,
    chart_request_params,
    interface,
) -> ChartResult:
    """Validates and produces a `ChartResult` model containing all the deliverables for that chart

    Args:
        chart_request_params: The requested chart plot
            parameters encapsulated as a model
        interface: The charts interface class
            which must implement the
            `generate_chart_output()` method

    Returns:
        An enriched `ChartResult` model
        which holds the chart figure amongst
        other key deliverables for the chart

    Raises:
        `InvalidPlotParametersError`: If an underlying
            validation check has failed.
            This could be because there is
            an invalid topic and metric selection.
            Or because the selected dates are not in
            the expected chronological order.
        `DataNotFoundForAnyPlotError`: If no plots
            returned any data from the underlying queries

    """
    charts_interface = interface(chart_request_params=chart_request_params)
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return ChartResult(
        last_updated=charts_interface.last_updated,
        chart=_encode_figure(
            figure=chart_output.figure, file_format=chart_request_params.file_format
        ),
        alt_text=chart_output.description,
        figure=chart_output.interactive_chart_figure_output,
    )


def _encode_figure(*, figure: plotly.graph_objects.Figure, file_format: str) -> str:
    """URI Encode the supplied chart figure

    Args:
        figure: The plotly `Figure` object a chart figure
        file_format: The format to which the file
            should be converted into

    Returns:
        An encoded string representation of the figure

    """
    if file_format != "svg":
        raise ValueError

    optimized_svg: str = _create_optimized_svg(figure=figure, file_format=file_format)
    return urllib.parse.quote_plus(optimized_svg)


def _create_optimized_svg(
    *, figure: plotly.graph_objects.Figure, file_format: str
) -> str:
    """Convert figure to an optimized `svg`

    Args:
        figure: The plotly `Figure` object a chart figure
        file_format: The format to which the file
            should be converted into

    Returns:
        The figure as an image and optimized for size if required

    """
    svg_image: bytes = figure.to_image(format=file_format, validate=False)
    return scour.scourString(in_string=svg_image)


def generate_chart_as_file(
    *,
    chart_request_params,
    interface,
) -> bytes:
    """Validates and produces a bytes string which represents the chart image in memory

    Args:
        chart_request_params: The requested chart plot
            parameters encapsulated as a model
        interface: The charts interface class
            which must implement the
            `generate_chart_output()` method

    Returns:
        A bytes string representation of the chart image

    Raises:
        `InvalidPlotParametersError`: If an underlying
            validation check has failed.
            This could be because there is
            an invalid topic and metric selection.
            Or because the selected dates are not in
            the expected chronological order.
        `DataNotFoundForAnyPlotError`: If no plots
            returned any data from the underlying queries

    """
    charts_interface = interface(chart_request_params=chart_request_params)
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return _write_figure(
        figure=chart_output.figure, file_format=chart_request_params.file_format
    )


def _write_figure(*, figure: plotly.graph_objects.Figure, file_format: str) -> bytes:
    """Convert a figure to a static image and write to a file in the desired image format

    Args:
        figure: The figure object or a dictionary representing a figure
        file_format: The format to which the file
            should be converted into

    Returns:
        The image in memory

    """
    file = io.BytesIO()

    figure.write_image(
        file=file,
        format=file_format,
        validate=False,
    )

    file.seek(0)
    return file.getvalue()
