import urllib.parse
from datetime import datetime

import plotly.graph_objects
from django.db.models import Manager
from scour import scour

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import (
    bar,
    line,
    line_multi_coloured,
    line_with_shaded_section,
    waffle,
)
from metrics.domain.models import PlotData, PlotsCollection
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts import calculations
from metrics.interfaces.plots.access import PlotsInterface

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class InvalidFileFormatError(Exception):
    def __init__(self):
        message = "Invalid file format, must be `svg`"
        super().__init__(message)


class ChartsInterface:
    def __init__(
        self,
        chart_plots: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: PlotsInterface | None = None,
    ):
        self.chart_plots = chart_plots
        self.chart_type = self.chart_plots.plots[0].chart_type
        self.core_time_series_manager = core_time_series_manager

        self.plots_interface = plots_interface or PlotsInterface(
            plots_collection=self.chart_plots,
            core_time_series_manager=core_time_series_manager,
        )

        self._latest_date: str = ""

    def generate_chart_figure(self) -> plotly.graph_objects.Figure:
        """Creates the chart figure dictated the instance variable of `chart_type`

        Returns:
            A plotly `Figure` object for the created chart

        """
        if self.chart_type == ChartTypes.waffle.value:
            raise NotImplementedError

        if self.chart_type == ChartTypes.simple_line.value:
            return self.generate_simple_line_chart()

        if self.chart_type == ChartTypes.bar.value:
            return self.generate_bar_chart()

        if self.chart_type == ChartTypes.line_multi_coloured.value:
            return self.generate_line_multi_coloured_chart()

        return self.generate_line_with_shaded_section_chart()

    def generate_waffle_chart(self) -> plotly.graph_objects.Figure:
        """Creates a waffle chart figure for the requested chart plot

        Returns:
            A plotly `Figure` object for the created waffle chart

        """
        plot_parameters = self.chart_plots.plots[0]
        value = self.core_time_series_manager.get_latest_metric_value(
            topic_name=plot_parameters.topic_name,
            metric_name=plot_parameters.metric_name,
        )
        return waffle.generate_chart_figure([value])

    def generate_simple_line_chart(self) -> plotly.graph_objects.Figure:
        """Creates a simple line chart figure for the requested chart plot

        Returns:
            A plotly `Figure` object for the created simple line chart

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width

        plots_data: list[PlotData] = self.build_chart_plots_data()
        plot_data: PlotData = plots_data[0]
        return line.generate_chart_figure(
            chart_height=chart_height,
            chart_width=chart_width,
            y_axis_values=plot_data.y_axis_values,
        )

    def generate_bar_chart(self) -> plotly.graph_objects.Figure:
        """Creates a bar chart figure for the requested chart plot

        Notes
            This does support **multiple** plots on the same figure

        Returns:
            A plotly `Figure` object for the created bar chart

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        plots_data: list[PlotData] = self.build_chart_plots_data()

        return bar.generate_chart_figure(
            chart_height=chart_height,
            chart_width=chart_width,
            chart_plots_data=plots_data,
        )

    def generate_line_multi_coloured_chart(self) -> plotly.graph_objects.Figure:
        """Creates a multiple line colour-differentiated chart figure for the requested chart plots

        Notes
            This does support **multiple** plots on the same figure

        Returns:
            A plotly `Figure` object for the created multi-coloured line chart

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries
        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        plots_data: list[PlotData] = self.build_chart_plots_data()

        return line_multi_coloured.generate_chart_figure(
            chart_height=chart_height,
            chart_width=chart_width,
            chart_plots_data=plots_data,
        )

    def generate_line_with_shaded_section_chart(self) -> plotly.graph_objects.Figure:
        """Creates a line chart with shaded section figure for the requested chart plot

        Notes:
            Currently on the first requested chart plot is used,
            the remaining plots are not applied to the figure.

        Returns:
            A plotly `Figure` object for the created line chart with shaded section

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries
        """
        plots_data: list[PlotData] = self.build_chart_plots_data()
        params = self.param_builder_for_line_with_shaded_section(plots_data=plots_data)

        return line_with_shaded_section.generate_chart_figure(**params)

    def build_chart_plots_data(self) -> list[PlotData]:
        """Creates a list of `PlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and an enriched model is not provided.

        Returns:
            A list of `PlotData` models for each of the requested chart plots.

        Raises:
            `DataNotFoundForAnyPlotError`: If no plots
                returned any data from the underlying queries

        """
        plots_data: list[PlotData] = self.plots_interface.build_plots_data()
        self._set_latest_date_from_plots_data(plots_data=plots_data)
        return plots_data

    def _set_latest_date_from_plots_data(self, plots_data: list[PlotData]) -> None:
        """Extracts the latest date from the list of given `plots_data`

        Notes:
            This extracted value is set on the `_latest_date`
            instance attribute on this object

        Args:
            plots_data: List of `PlotData` models,
                where each model represents a requested plot.
                Note that each `PlotData` model is enriched
                with the according x and y values along with
                requests parameters like colour and plot label.

        Returns:
            None

        """
        try:
            latest_date: datetime.date = max(plot.latest_date for plot in plots_data)
        except (ValueError, TypeError):
            return

        self._latest_date: str = datetime.strftime(latest_date, "%Y-%m-%d")

    def param_builder_for_line_with_shaded_section(self, plots_data: list[PlotData]):
        plot_data = plots_data[0]
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        x_axis_values = plot_data.x_axis_values
        y_axis_values = plot_data.y_axis_values
        metric_name = plot_data.parameters.metric_name

        return {
            "plots_data": plots_data,
            "chart_height": chart_height,
            "chart_width": chart_width,
            "x_axis_values": x_axis_values,
            "y_axis_values": y_axis_values,
            "metric_name": metric_name,
            "change_in_metric_value": self.calculate_change_in_metric_value(
                values=y_axis_values,
                metric_name=metric_name,
            ),
            "rolling_period_slice": calculations.get_rolling_period_slice_for_metric(
                metric_name=metric_name
            ),
        }

    def create_optimized_svg(self, figure: plotly.graph_objects.Figure) -> str:
        """Convert figure to a `svg` then optimize the size of it

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            A figure as an image and optimized for size if required
        """
        svg_image = figure.to_image(format=self.chart_plots.file_format, validate=False)
        return scour.scourString(in_string=svg_image)

    def encode_figure(self, figure: plotly.graph_objects.Figure) -> str:
        """
        URI Encode the supplied chart figure

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            An encoded string representation of the figure

        """
        if self.chart_plots.file_format != "svg":
            raise InvalidFileFormatError

        optimized_svg: str = self.create_optimized_svg(figure=figure)

        encoded_chart: str = urllib.parse.quote_plus(optimized_svg)

        return encoded_chart

    def write_figure(self, figure: plotly.graph_objects.Figure) -> str:
        """
        Convert a figure to a static image and write to a file in the desired image format

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            The filename of the image

        """
        filename = f"new_chart.{self.chart_plots.file_format}"
        figure.write_image(
            file=filename, format=self.chart_plots.file_format, validate=False
        )

        return filename

    @staticmethod
    def calculate_change_in_metric_value(values, metric_name) -> int | float:
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )
        preceding_slice: int = rolling_period_slice * 2

        values = values[-preceding_slice:]

        return calculations.change_between_each_half(values=values)

    def get_encoded_chart(self, figure: plotly.graph_objects.Figure) -> dict[str, str]:
        """Creates a dict containing a timestamp for the last data point + encoded string for the chart figure.

        Args:
            figure: Plotly figure or figure dictionary

        Returns:
            A dict containing:
             "last_updated": A timestamp for the last data point
             "chart": An encoded string representing the chart figure

        """
        return {
            "last_updated": self._latest_date,
            "chart": self.encode_figure(figure=figure),
        }


def generate_chart_as_file(chart_plots: PlotsCollection) -> str:
    """Validates and creates a chart figure based on the parameters provided within the `chart_plots` model

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        The filename of the created image

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
    charts_interface = ChartsInterface(chart_plots=chart_plots)
    figure: plotly.graph_objects.Figure = charts_interface.generate_chart_figure()

    return charts_interface.write_figure(figure=figure)


def generate_encoded_chart(chart_plots: PlotsCollection) -> dict[str, str]:
    """Validates and creates a chart figure based on the parameters provided within the `chart_plots` model
     Then encodes it, adds the last_updated_date to it and returns the result as a serialized JSON string

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        A dict containing:
         "last_updated": A timestamp for the last data point
         "chart": An encoded string representing the chart figure

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
    charts_interface = ChartsInterface(chart_plots=chart_plots)
    figure: plotly.graph_objects.Figure = charts_interface.generate_chart_figure()

    return charts_interface.get_encoded_chart(figure=figure)
