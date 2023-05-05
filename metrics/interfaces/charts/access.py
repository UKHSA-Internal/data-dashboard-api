import datetime
from typing import Dict, List, Optional, Union

import plotly.graph_objects
from django.db.models import Manager

from metrics.data.access.core_models import (
    get_date_n_months_ago_from_timestamp,
    unzip_values,
)
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import (
    bar,
    line,
    line_multi_coloured,
    line_with_shaded_section,
    waffle,
)
from metrics.domain.models import ChartPlotData, ChartPlotParameters, ChartPlots
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts import calculations, validation

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class ChartsInterface:
    def __init__(
        self,
        chart_plots: ChartPlots,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.chart_plots_parameters = chart_plots
        self.chart_type = self.chart_plots_parameters.plots[0].chart_type
        self.core_time_series_manager = core_time_series_manager

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
            return self.generate_line_multi_coloured()

        return self.generate_line_with_shaded_section_chart()

    def generate_waffle_chart(self) -> plotly.graph_objects.Figure:
        """Creates a waffle chart figure for the requested chart plot

        Returns:
            A plotly `Figure` object for the created waffle chart

        """
        plot_parameters = self.chart_plots_parameters.plots[0]
        value = self.core_time_series_manager.get_latest_metric_value(
            topic=plot_parameters.topic,
            metric_name=plot_parameters.metric,
        )
        return waffle.generate_chart_figure([value])

    def generate_simple_line_chart(self) -> plotly.graph_objects.Figure:
        """Creates a simple line chart figure for the requested chart plot

        Returns:
            A plotly `Figure` object for the created simple line chart

        """
        plots_data: List[ChartPlotData] = self._build_chart_plots_data()
        plot_data: ChartPlotData = plots_data[0]
        return line.generate_chart_figure(plot_data.y_axis)

    def generate_bar_chart(self) -> plotly.graph_objects.Figure:
        """Creates a bar chart figure for the requested chart plot

        Returns:
            A plotly `Figure` object for the created bar chart

        """
        plots_data: List[ChartPlotData] = self._build_chart_plots_data()
        plot_data: ChartPlotData = plots_data[0]

        return bar.generate_chart_figure(
            dates=plot_data.x_axis,
            values=plot_data.y_axis,
            legend=plot_data.parameters.metric,
        )

    def generate_line_multi_coloured(self) -> plotly.graph_objects.Figure:
        """Creates a multiple line colour-differentiated chart figure for the requested chart plots

        Notes
            This does support **multiple** plots on the same figure

        Returns:
            A plotly `Figure` object for the created multi-coloured line chart

        """
        plots_data: List[ChartPlotData] = self._build_chart_plots_data()
        return line_multi_coloured.generate_chart_figure(plots_data)

    def generate_line_with_shaded_section_chart(self) -> plotly.graph_objects.Figure:
        """Creates a line chart with shaded section figure for the requested chart plot

        Notes:
            Currently on the first requested chart plot is used,
            the remaining plots are not applied to the figure.

        Returns:
            A plotly `Figure` object for the created line chart with shaded section

        """
        plots_data: List[ChartPlotData] = self._build_chart_plots_data()
        plot_data: ChartPlotData = plots_data[0]
        params = self.param_builder_for_line_with_shaded_section(plot_data=plot_data)

        return line_with_shaded_section.generate_chart_figure(**params)

    def _build_chart_plots_data(self) -> List[ChartPlotData]:
        """Creates a list of `ChartPlotData` models which hold the params and corresponding data for the requested plots

        Notes:
            The corresponding timeseries data is used to enrich a
            pydantic model which also holds the corresponding params.
            These models can then be passed into the domain libraries.

            If no data is returned for a particular plot,
            that chart plot is skipped and an enriched model is not provided.

        Returns:
            List[ChartPlotData]: A list of `ChartPlotData` models for
                each of the requested chart plots.

        """
        plots_data = []
        for chart_plot_parameters in self.chart_plots_parameters.plots:
            chart_plot_parameters: ChartPlotParameters
            timeseries_queryset = self.get_timeseries_for_chart_plot_parameters(
                chart_plot_parameters=chart_plot_parameters
            )

            try:
                dates, values = unzip_values(timeseries_queryset)
            except ValueError:
                continue
            else:
                chart_plot_data = ChartPlotData(
                    parameters=chart_plot_parameters,
                    x_axis=dates,
                    y_axis=values,
                )
                plots_data.append(chart_plot_data)

        return plots_data

    def get_timeseries_for_chart_plot_parameters(
        self, chart_plot_parameters: ChartPlotParameters
    ):
        """Returns the timeseries records for the requested plot as a QuerySet

        Notes:
            If no `date_from` was provided within the `chart_plot_parameters`,
            then a default of 1 year from the current date will be used.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers.
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        plot_params: Dict[str, str] = chart_plot_parameters.to_dict_for_query()
        date_from: str = make_datetime_from_string(
            date_from=chart_plot_parameters.date_from
        )

        return self.get_timeseries(
            **plot_params,
            date_from=date_from,
        )

    def get_timeseries(
        self,
        topic: str,
        metric: str,
        date_from: datetime.date,
        geography: Optional[str] = None,
        geography_type: Optional[str] = None,
        stratum: Optional[str] = None,
    ):
        """Gets the time series for the `metric` and `topic` from the `date_from` stamp.

        Notes:
            Additional filtering is available via the following optional params:
             - `geography`
             - `geography_type`
             - `stratum`

        Args:
            topic: The name of the disease being queried.
                E.g. `COVID-19`
            metric: The name of the metric being queried.
                E.g. `new_cases_7days_sum
            date_from: The datetime object to begin the query from.
                E.g. datetime.datetime(2023, 3, 27, 0, 0, 0, 0)
                would strip off any records which occurred before that date.
            geography: The name of the geography to apply additional filtering to.
                E.g. `England`
            geography_type: The name of the type of geography to apply additional filtering.
                E.g. `Nation`
            stratum: The value of the stratum to apply additional filtering to.
                E.g. `0_4`, which would be used to capture the age group 0 to 4 years old.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        return self.core_time_series_manager.filter_for_dates_and_values(
            topic=topic,
            metric=metric,
            date_from=date_from,
            geography=geography,
            geography_type=geography_type,
            stratum=stratum,
        )

    def param_builder_for_line_with_shaded_section(self, plot_data: ChartPlotData):
        dates = plot_data.x_axis
        values = plot_data.y_axis
        metric_name = plot_data.parameters.metric

        return {
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


def make_datetime_from_string(date_from: Optional[str]) -> datetime.datetime:
    """Parses the `date_from` string into a datetime object. Defaults to 1 year ago from the current date.

    Args:
        date_from: A string representing the date in the format `%Y-%m-%d`
            E.g. "2022-10-01"

    Returns:
        `datetime` object representing the `date_from` string
            or a default of 1 year ago from the current date.

    """
    try:
        return datetime.datetime.strptime(date_from, "%Y-%m-%d")
    except (TypeError, ValueError):
        one_year = 12
        return get_date_n_months_ago_from_timestamp(
            datetime_stamp=datetime.date.today(), number_of_months=one_year
        )


def generate_chart(chart_plots: ChartPlots) -> str:
    """Validates and creates a chart figure based of the parameters provided within the `chart_plots` model

    Args:
        chart_plots: The requested chart plots parameters
            encapsulated as a model

    Returns:
        The filename of the created image

    """
    _validate_each_requested_chart_plot(chart_plots=chart_plots)

    library = ChartsInterface(chart_plots=chart_plots)
    figure = library.generate_chart_figure()

    return write_figure(
        figure=figure,
        topic="-",
        file_format=chart_plots.file_format,
    )


def _validate_each_requested_chart_plot(chart_plots: ChartPlots) -> None:
    for chart_plot_params in chart_plots.plots:
        chart_plot_params: ChartPlotParameters

        date_from = make_datetime_from_string(date_from=chart_plot_params.date_from)
        charts_request_validator = validation.ChartsRequestValidator(
            topic=chart_plot_params.topic,
            metric=chart_plot_params.metric,
            chart_type=chart_plot_params.chart_type,
            date_from=date_from,
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
