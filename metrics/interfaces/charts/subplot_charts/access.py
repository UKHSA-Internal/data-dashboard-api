import io

import plotly.graph_objects
from django.db.models.manager import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts.subplots import generate_chart_figure
from metrics.domain.models import SubplotChartGenerationPayload, SubplotGenerationData
from metrics.domain.models.charts.subplot_charts import SubplotChartRequestParameters
from metrics.interfaces.charts.common.chart_output import ChartOutput
from metrics.interfaces.plots.access import PlotGenerationData, PlotsInterface

DEFAULT_SUBPLOT_CHART_TYPE = "bar"


class SubplotChartsInterface:
    last_updated = "2025-01-01"

    def __init__(
        self,
        *,
        chart_request_params: SubplotChartRequestParameters,
        core_time_series_manager: type[Manager] = CoreTimeSeries.objects,
    ):
        self.chart_request_params = chart_request_params
        self.chart_type = DEFAULT_SUBPLOT_CHART_TYPE
        self.core_time_series_manager = core_time_series_manager

    def _build_plots_data(self) -> list[dict[str, PlotGenerationData | str]]:
        """Creates a list of `Subplot` models which hold the params and corresponding data for the
            requested subplots and each subplot's `PlotGenerationData`.

        Notes:
            The corresponding timeseries data is used to enrich a pydantic
            model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

        Returns:
            A list of `SubplotGenerationData` models for each of the requested `Subplots`
            and their individual `Plots`.

        """
        subplots_data: list[dict[str, PlotGenerationData | str]] = []

        for subplot in self.chart_request_params.subplots:
            plots_interface = PlotsInterface(chart_request_params=subplot)
            subplot_data: PlotGenerationData = plots_interface.build_plots_data()
            subplots_data.append(
                {
                    "subplot_title": subplot.subplot_title,
                    "subplot_data": subplot_data,
                }
            )

        return subplots_data

    def _build_chart_generation_payload(self) -> SubplotChartGenerationPayload:
        """Creates a `SubplotChartGenerationPayload` model for chart generation

        Returns:
            An enriched `SubplotChartGenerationPayload` model that holds the
            corresponding parameters to build a subplot chart.
        """
        subplots_data: SubplotGenerationData = self._build_plots_data()
        return SubplotChartGenerationPayload(
            subplot_data=subplots_data,
            chart_width=self.chart_request_params.chart_width,
            chart_height=self.chart_request_params.chart_height,
            x_axis_title=self.chart_request_params.x_axis_title,
            y_axis_title=self.chart_request_params.y_axis_title,
            y_axis_minimum_value=self.chart_request_params.y_axis_minimum_value,
            y_axis_maximum_value=self.chart_request_params.y_axis_maximum_value,
        )

    @staticmethod
    def _build_chart_figure(
        chart_generation_payload: SubplotChartGenerationPayload,
    ) -> plotly.graph_objects.Figure:
        """Build a plotly chart `Figure` object for a `Subplot` chart.

        Args:
            chart_generation_payload: An enriched `SubplotChartGenerationPayload` model
            which holds all the parameters required to generate the chart.
            These include x and y values, colour information and label text.

        Returns:
            A plotly `Figure` object for the created subplot chart.
        """
        return generate_chart_figure(
            chart_generation_payload=chart_generation_payload,
        )

    def generate_chart_output(self):
        """Generates a `plotly` chart figure and a corresponding description

        Returns:
            An enriched `ChartOutput` model containing:
            A plotly `Figure` of the created chart and its description which
            summarises the produced chart.
        """
        chart_generation_payload: SubplotChartGenerationPayload = (
            self._build_chart_generation_payload()
        )

        figure = self._build_chart_figure(
            chart_generation_payload=chart_generation_payload,
        )

        # Temporary chart description - there is a follow on ticket to implement
        chart_description = "Subplot chart comparing multiple metrics"

        return ChartOutput(
            figure=figure,
            description=chart_description,
            is_headline=False,
        )

    def write_figure(self, *, figure: plotly.graph_objects.Figure) -> bytes:
        """
        Convert a figure to a static image and write to a file in the desired image format

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            The image in memory

        """
        file = io.BytesIO()

        figure.write_image(
            file=file,
            format=self.chart_request_params.file_format,
            validate=False,
        )

        file.seek(0)
        return file.getvalue()


def generate_chart_file(
    *, chart_request_params: SubplotChartRequestParameters
) -> bytes:
    charts_interface = SubplotChartsInterface(chart_request_params=chart_request_params)
    chart_output: ChartOutput = charts_interface.generate_chart_output()

    return charts_interface.write_figure(figure=chart_output.figure)
