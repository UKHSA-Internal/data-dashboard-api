import datetime
from typing import Optional, Union

import plotly.graph_objects
from django.db.models import Manager

from metrics.data.access.core_models import (
    get_date_n_months_ago_from_timestamp,
    unzip_values,
)
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import line, line_with_shaded_section, waffle
from metrics.domain.models import ChartsPlotParameters
from metrics.domain.utils import ChartTypes
from metrics.interfaces.charts import calculations, validation

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class ChartsInterface:
    def __init__(
        self,
        topic: str,
        metric: str,
        chart_type: str,
        date_from: datetime.datetime,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.topic = topic
        self.metric = metric
        self.chart_type = chart_type.lower()
        self.date_from = date_from
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

        return self.generate_line_with_shaded_section_chart()

    def generate_waffle_chart(self) -> plotly.graph_objects.Figure:
        """Creates a waffle chart figure for the `metric` instance variable

        Returns:
            A plotly `Figure` object for the created waffle chart

        """
        values = self.core_time_series_manager.get_latest_metric_value()
        return waffle.generate_chart_figure(values)

    def generate_simple_line_chart(self) -> plotly.graph_objects.Figure:
        """Creates a simple line chart figure for the `metric` instance variable

        Returns:
            A plotly `Figure` object for the created simple line chart

        """
        timeseries_queryset = self.get_timeseries()
        _, values = unzip_values(values=timeseries_queryset)
        return line.generate_chart_figure(values)

    def generate_line_with_shaded_section_chart(self) -> plotly.graph_objects.Figure:
        """Creates a line chart with shaded section figure for the `metric` instance variable

        Returns:
            A plotly `Figure` object for the created line chart with shaded section

        """
        params = self.param_builder_for_line_with_shaded_section()

        return line_with_shaded_section.generate_chart_figure(
            **params,
        )

    def get_timeseries(self):
        """Gets the time series for the `metric` and `topic` from the `date_from` stamp.

        Returns:
            QuerySet: An ordered queryset from oldest -> newest
                of the (dt, metric_value) numbers:
                Examples:
                    `<CoreTimeSeriesQuerySet [
                        (datetime.date(2022, 10, 10), Decimal('0.8')),
                        (datetime.date(2022, 10, 17), Decimal('0.9'))
                    ]>`

        """
        return self.core_time_series_manager.by_topic_metric_for_dates_and_values(
            topic=self.topic,
            metric_name=self.metric,
            date_from=self.date_from,
        )

    def param_builder_for_line_with_shaded_section(self):
        timeseries_queryset = self.get_timeseries()
        dates, values = unzip_values(values=timeseries_queryset)

        return {
            "dates": dates,
            "values": values,
            "metric_name": self.metric,
            "change_in_metric_value": self.calculate_change_in_metric_value(
                values=values
            ),
            "rolling_period_slice": calculations.get_rolling_period_slice_for_metric(
                metric_name=self.metric
            ),
        }

    def calculate_change_in_metric_value(self, values) -> Union[int, float]:
        rolling_period_slice: int = calculations.get_rolling_period_slice_for_metric(
            metric_name=self.metric
        )
        preceding_slice: int = rolling_period_slice * 2

        values = values[-preceding_slice:]

        return calculations.change_between_each_half(values=values)


def make_datetime_from_string(date_from: Optional[str]) -> datetime.datetime:
    """Parses the `date_from` string into a datetime object. Defaults to 1 year ago from the current date.

    Args:
        date_from: A datestring in the format `%Y-%m-%d`

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


def generate_chart(
    chart_plot_model: ChartsPlotParameters,
    file_format: str,
):
    date_from = make_datetime_from_string(date_from=chart_plot_model.date_from)
    charts_request_validator = validation.ChartsRequestValidator(
        topic=chart_plot_model.topic,
        metric=chart_plot_model.metric,
        chart_type=chart_plot_model.chart_type,
        date_from=date_from,
    )
    charts_request_validator.validate()

    library = ChartsInterface(
        topic=chart_plot_model.topic,
        metric=chart_plot_model.metric,
        chart_type=chart_plot_model.chart_type,
        date_from=date_from,
    )
    figure = library.generate_chart_figure()

    return write_figure(
        figure=figure,
        topic=f"{chart_plot_model.topic}.{chart_plot_model.metric}",
        file_format=file_format,
    )


def write_figure(
    figure: plotly.graph_objects.Figure, topic: str, file_format: str
) -> str:
    """
    Convert a figure to a static image and write to a file in the desired image format

    Args:
        figure: The figure object or a dictioanry representing a figure
        topic: The required topic (eg. COVID-19)
        file_format: The required file format (eg svg, jpeg)

    Returns:
        The filename of the image
    """

    filename = f"{topic}.{file_format}"
    figure.write_image(file=filename, format=file_format)

    return filename
