from enum import Enum
from typing import Dict, List, Optional, Union

import plotly.graph_objects
from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import (
    bar,
    line,
    line_multi_coloured,
    line_with_shaded_section,
    waffle,
)
from metrics.domain.models import PlotParameters, PlotsCollection, PlotsData
from metrics.domain.tables.generation import create_plots_in_tabular_format
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

        plots_data: List[PlotsData] = self.build_chart_plots_data()
        plot_data: PlotsData = plots_data[0]
        return line.generate_chart_figure(
            chart_height=chart_height,
            chart_width=chart_width,
            values=plot_data.y_axis,
        )

    def generate_bar_chart(self) -> plotly.graph_objects.Figure:
        """Creates a bar chart figure for the requested chart plot

        Returns:
            A plotly `Figure` object for the created bar chart

        """
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        plots_data: List[PlotsData] = self.build_chart_plots_data()
        plot_data: PlotsData = plots_data[0]

        return bar.generate_chart_figure(
            chart_height=chart_height,
            chart_width=chart_width,
            dates=plot_data.x_axis,
            values=plot_data.y_axis,
            legend=plot_data.parameters.metric_name,
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
        plots_data: List[PlotsData] = self.build_chart_plots_data()

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
        plots_data: List[PlotsData] = self.build_chart_plots_data()
        plot_data: PlotsData = plots_data[0]
        params = self.param_builder_for_line_with_shaded_section(plot_data=plot_data)

        return line_with_shaded_section.generate_chart_figure(**params)

    def generate_plots_for_table(self) -> List[Dict[str, str]]:
        """Create a list of plots from the request

        Returns:
            The requested plots in tabular format
        """
        plots_data: List[PlotsData] = self.build_chart_plots_data()

        return create_plots_in_tabular_format(
            tabular_plots_data=plots_data,
        )

    def build_chart_plots_data(self) -> List[PlotsData]:
        """Creates a list of `ChartPlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and an enriched model is not provided.

        Returns:
            List[PlotsData]: A list of `ChartPlotData` models for
                each of the requested chart plots.

        """
        return self.plots_interface.build_plots_data()

    def param_builder_for_line_with_shaded_section(self, plot_data: PlotsData):
        chart_height = self.chart_plots.chart_height
        chart_width = self.chart_plots.chart_width
        dates = plot_data.x_axis
        values = plot_data.y_axis
        metric_name = plot_data.parameters.metric_name

        return {
            "chart_height": chart_height,
            "chart_width": chart_width,
            "dates": dates,
            "values": values,
            "metric_name": metric_name,
            "change_in_metric_value": self.calculate_change_in_metric_value(
                values=values,
                metric_name=metric_name,
            ),
            "rolling_period_slice": calculations.get_rolling_period_slice_for_metric(
                metric_name=metric_name
            ),
        }

    @staticmethod
    def calculate_change_in_metric_value(values, metric_name) -> Union[int, float]:
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=metric_name
        )
        preceding_slice: int = rolling_period_slice * 2

        values = values[-preceding_slice:]

        return calculations.change_between_each_half(values=values)


def generate_chart(chart_plots: PlotsCollection) -> str:
    """Validates and creates a chart figure based of the parameters provided within the `chart_plots` model

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        The filename of the created image

    """
    validate_each_requested_chart_plot(chart_plots=chart_plots)

    library = ChartsInterface(chart_plots=chart_plots)
    figure = library.generate_chart_figure()

    return write_figure(
        figure=figure,
        topic="-",
        file_format=chart_plots.file_format,
    )


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


def write_figure(
    figure: plotly.graph_objects.Figure, topic: str, file_format: str
) -> str:
    """
    Convert a figure to a static image and write to a file in the desired image format

    Args:
        figure: The figure object or a dictionary representing a figure
        topic: The required topic (eg. COVID-19)
        file_format: The required file format (eg svg, jpeg)

    Returns:
        The filename of the image

    """
    filename = f"{topic}.{file_format}"
    figure.write_image(file=filename, format=file_format)

    return filename


class ChartAxisFields(Enum):
    stratum = "stratum__name"
    date = "dt"
    metric = "metric_value"
    geography = "geography__geography_type__name"

    @classmethod
    def choices(cls):
        return tuple((field_name.name, field_name.name) for field_name in cls)

    def __str__(self):
        return str(self.value)
