import datetime
from typing import Callable, Dict

from django.db.models import Manager

from metrics.data.access.core_models import (
    unzip_values,
)
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts import line, line_with_shaded_section, waffle

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


CHART_BUILDERS: Dict[str, callable] = {
    "simple_line_graph": line.generate_chart_figure,
    "waffle": waffle.generate_chart_figure,
    "line_with_shaded_section": line_with_shaded_section.generate_chart_figure,
}


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
        self.chart_type = chart_type
        self.date_from = date_from

        self.core_time_series_manager = core_time_series_manager

    def get_chart_builder(self) -> Callable:
        return CHART_BUILDERS[self.chart_type.lower()]

    def generate_chart_figure(self):
        chart_builder = self.get_chart_builder()

        if self.chart_type == "waffle":
            values = self.get_latest_metric_value()
            figure = chart_builder([values])

        else:

            timeseries_queryset = self.get_time_series_metric_values()

            dates, values = unzip_values(timeseries_queryset)

            if self.chart_type == "simple_line_graph":
                figure = chart_builder(values)
            else:
                rolling_period_slice = 1 if "weekly" in self.metric else 7
                figure = chart_builder(
                    dates, values, self.metric, 10, rolling_period_slice
                )

        return figure

    def get_latest_metric_value(self):
        return self.core_time_series_manager.get_latest_metric_value(
            topic=self.topic,
            metric_name=self.metric,
        )

    def get_time_series_metric_values(self):

        return self.core_time_series_manager.by_topic_metric_for_dates_and_values(
            topic=self.topic,
            metric_name=self.metric,
            date_from=self.date_from,
        )

