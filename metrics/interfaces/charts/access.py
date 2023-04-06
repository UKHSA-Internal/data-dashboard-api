import datetime
from enum import Enum

import plotly.graph_objects
from django.db.models import Manager

from metrics.data.access.core_models import unzip_values
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import line, line_with_shaded_section, waffle

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class ChartTypes(Enum):
    simple_line_graph = "simple_line_graph"
    waffle = "waffle"
    line_with_shaded_section = "line_with_shaded_section"

    @classmethod
    def choices(cls):
        return tuple((chart_type.value, chart_type.value) for chart_type in cls)


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

    def generate_chart_figure(self):
        if self.chart_type == ChartTypes.waffle.value:
            return self.generate_waffle_chart()

        if self.chart_type == ChartTypes.simple_line_graph.value:
            return self.generate_simple_line_chart()

        return self.generate_line_with_shaded_section_chart()

    def generate_waffle_chart(self) -> plotly.graph_objects.Figure:
        values = self.core_time_series_manager.get_latest_metric_value()
        return waffle.generate_chart_figure(values)

    def generate_simple_line_chart(self) -> plotly.graph_objects.Figure:
        timeseries_queryset = self.get_timeseries()
        _, values = unzip_values(values=timeseries_queryset)
        return line.generate_chart_figure(values)

    def generate_line_with_shaded_section_chart(self):
        timeseries_queryset = self.get_timeseries()
        dates, values = unzip_values(values=timeseries_queryset)

        return line_with_shaded_section.generate_chart_figure(
            dates=dates,
            values=values,
            metric_name=self.metric,
            change_in_metric_value=10,
            rolling_period_slice=1 if "weekly" in self.metric else 7,
        )

    def get_timeseries(self):
        return self.core_time_series_manager.by_topic_metric_for_dates_and_values(
            topic=self.topic,
            metric_name=self.metric,
            date_from=self.date_from,
        )
