import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Union

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
from metrics.domain.models import PlotParameters, PlotsCollection, PlotData
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts import calculations, validation
from metrics.interfaces.plots.access import PlotsInterface

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class ChartsInterface:
    def __init__(
        self,
        chart_plots: PlotsCollection,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        plots_interface: Optional[PlotsInterface] = None,
    ):
        self.chart_plots = chart_plots
        self.chart_type = self.chart_plots.plots[0].chart_type
        self.core_time_series_manager = core_time_series_manager

        self.plots_interface = plots_interface or PlotsInterface(
            plots_collection=self.chart_plots,
            core_time_series_manager=core_time_series_manager,
        )

    def generate_chart_figure(self) -> plotly.graph_objects.Figure:
        """Creates the chart figure dictated the instance variable of `chart_type`

        Returns:
            A plotly `Figure` object for the created chart

        """
        if self.chart_type == ChartTypes.waffle.value:
            return self.generate_waffle_chart()

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

        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width

        plots_data: List[PlotData] = self.build_chart_plots_data()
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

        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        plots_data: List[PlotData] = self.build_chart_plots_data()

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

        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        plots_data: List[PlotData] = self.build_chart_plots_data()

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

        """
        plots_data: List[PlotData] = self.build_chart_plots_data()
        plot_data: PlotData = plots_data[0]
        params = self.param_builder_for_line_with_shaded_section(plot_data=plot_data)

        return line_with_shaded_section.generate_chart_figure(**params)

    def build_chart_plots_data(self) -> List[PlotData]:
        """Creates a list of `PlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and an enriched model is not provided.

        Returns:
            List[PlotData]: A list of `PlotData` models for
                each of the requested chart plots.

        """
        return self.plots_interface.build_plots_data()

    def param_builder_for_line_with_shaded_section(self, plot_data: PlotData):
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        x_axis_values = plot_data.x_axis_values
        y_axis_values = plot_data.y_axis_values
        metric_name = plot_data.parameters.metric_name

        return {
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

    def get_last_updated(self, figure: plotly.graph_objects.Figure) -> str:
        """
        If the chart has dates along the x-axis then extract the last dates from each plot
        and return the latest date of all of them

        Args:
            figure: The generated plotly chart

        Returns:
            The last date in the chart if applicable
        """
        last_date = ""

        if figure.layout.xaxis.type == "date":
            last_dates = []

            for trace in figure.data:
                last_dates.append(max(trace.x))

            # Now we have the end-dates from each of the plots, return the latest one
            # and convert datetime to a string
            last_date = datetime.strftime(max(last_dates), "%Y-%m-%d")

        return last_date

    def create_image_and_optimize_it(self, figure: plotly.graph_objects.Figure) -> str:
        """Convert figure to an image
           If the required image format is `svg` then optmimize the size of it
           else just return the image asis

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            A figure as an image and optimized for size if required
        """
        svg_image = figure.to_image(format=self.chart_plots.file_format)

        return (
            scour.scourString(in_string=svg_image)
            if self.chart_plots.file_format == "svg"
            else svg_image
        )

    def encode_figure(self, figure: plotly.graph_objects.Figure) -> str:
        """
        URI Encode the supplied chart figure

        Args:
            figure: The figure object or a dictionary representing a figure

        Returns:
            An encoded string representation of the figure
        """

        optimized_image = self.create_image_and_optimize_it(figure=figure)

        encoded_chart: str = urllib.parse.quote_plus(optimized_image)

        return encoded_chart

    def write_figure(self, figure: plotly.graph_objects.Figure, topic: str) -> str:
        """
        Convert a figure to a static image and write to a file in the desired image format

        Args:
            figure: The figure object or a dictionary representing a figure
            topic: The required topic (eg. COVID-19)

        Returns:
            The filename of the image

        """
        optimized_image = self.create_image_and_optimize_it(figure=figure)

        filename = f"{topic}.{self.chart_plots.file_format}"

        with open(filename, mode="wt") as f:
            f.write(optimized_image)

        return filename

    @staticmethod
    def calculate_change_in_metric_value(values, metric_name) -> Union[int, float]:
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )
        preceding_slice: int = rolling_period_slice * 2

        values = values[-preceding_slice:]

        return calculations.change_between_each_half(values=values)

    def get_encoded_chart(self, figure: plotly.graph_objects.Figure) -> Dict[str, str]:
        """Creates a dict containing a timestamp for the last data point + encoded string for the chart figure.

        Args:
            figure: Plotly figure or figure dictionary

        Returns:
            A dict containing:
             "last_updated": A timestamp for the last data point
             "chart": An encoded string representing the chart figure

        """
        return {
            "last_updated": self.get_last_updated(figure=figure),
            "chart": self.encode_figure(figure=figure),
        }


def generate_chart_as_file(chart_plots: PlotsCollection) -> str:
    """Validates and creates a chart figure based on the parameters provided within the `chart_plots` model

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        The filename of the created image

    """
    validate_each_requested_chart_plot(chart_plots=chart_plots)

    charts_interface = ChartsInterface(chart_plots=chart_plots)
    figure: plotly.graph_objects.Figure = charts_interface.generate_chart_figure()

    return charts_interface.write_figure(figure=figure, topic="-")


def generate_encoded_chart(chart_plots: PlotsCollection) -> Dict[str, str]:
    """Validates and creates a chart figure based on the parameters provided within the `chart_plots` model
     Then encodes it, adds the last_updated_date to it and returns the result as a serialized JSON string

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        A dict containing:
         "last_updated": A timestamp for the last data point
         "chart": An encoded string representing the chart figure

    """
    validate_each_requested_chart_plot(chart_plots=chart_plots)

    charts_interface = ChartsInterface(chart_plots=chart_plots)
    figure: plotly.graph_objects.Figure = charts_interface.generate_chart_figure()

    return charts_interface.get_encoded_chart(figure=figure)


def validate_each_requested_chart_plot(chart_plots: PlotsCollection) -> None:
    """Validates the request chart plots against the contents of the db

    Raises:
        `ChartTypeDoesNotSupportMetricError`: If the `metric` is not
            compatible for the required `chart_type`.
            E.g. A cumulative headline type number like `positivity_7days_latest`
            would not be viable for a line type (timeseries) chart.

        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `new_cases_daily` is currently only available
            for the topic of `COVID-19`

    """
    for chart_plot_params in chart_plots.plots:
        validate_chart_plot_parameters(chart_plot_parameters=chart_plot_params)


def validate_chart_plot_parameters(chart_plot_parameters: PlotParameters):
    """Validates the individual given `chart_plot_parameters` against the contents of the db

    Raises:
        `ChartTypeDoesNotSupportMetricError`: If the `metric` is not
            compatible for the required `chart_type`.
            E.g. A cumulative headline type number like `positivity_7days_latest`
            would not be viable for a line type (timeseries) chart.

        `MetricDoesNotSupportTopicError`: If the `metric` is not
            compatible for the required `topic`.
            E.g. `new_cases_daily` is currently only available
            for the topic of `COVID-19`

    """
    charts_request_validator = validation.ChartsRequestValidator(
        plot_parameters=chart_plot_parameters
    )
    charts_request_validator.validate()
