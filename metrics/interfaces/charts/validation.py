import datetime

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, Metric
from metrics.interfaces.charts.access import ChartTypes

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_METRIC_MANAGER = Metric.objects


class ChartTypeDoesNotSupportMetricError(Exception):
    ...


class MetricDoesNotSupportTopicError(Exception):
    ...


class ChartsRequestValidator:
    def __init__(
        self,
        topic: str,
        metric: str,
        chart_type: str,
        date_from: datetime.datetime,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
    ):
        self.topic = topic
        self.metric = metric
        self.chart_type = chart_type
        self.date_from = date_from
        self.core_time_series_manager = core_time_series_manager
        self.metric_manager = metric_manager

    def validate(self) -> None:
        """Validates the request against the contents of the db

        Returns:
            None

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
        self._validate_series_type_chart_works_with_metric()
        self._validate_metric_is_available_for_topic()

    def is_chart_series_type(self) -> bool:
        """Checks if the instance variable `chart_type` is of a timeseries type.

        Returns:
            bool: True if the `chart_type` can be used for timeseries data.
                False otherwise

        """
        if self.chart_type == ChartTypes.waffle.value:
            return False
        return True

    def _validate_series_type_chart_works_with_metric(self) -> None:
        requested_chart_is_series_type = self.is_chart_series_type()
        if not requested_chart_is_series_type:
            return

        metric_is_series_chart_compatible: bool = (
            self.does_metric_have_multiple_records()
        )
        if not metric_is_series_chart_compatible:
            raise ChartTypeDoesNotSupportMetricError(
                f"`{self.metric}` is not compatible with `{self.chart_type}` chart types"
            )

    def does_metric_have_multiple_records(self) -> bool:
        count: int = self.core_time_series_manager.get_count(
            topic=self.topic,
            metric_name=self.metric,
            date_from=self.date_from,
        )
        return count > 1

    def _validate_metric_is_available_for_topic(self) -> None:
        metric_is_topic_compatible: bool = self.does_metric_have_related_topic()

        if not metric_is_topic_compatible:
            raise MetricDoesNotSupportTopicError(
                f"`{self.topic}` does not have a corresponding metric of `{self.metric}`"
            )

    def does_metric_have_related_topic(self) -> bool:
        return self.metric_manager.is_metric_available_for_topic(
            metric_name=self.metric,
            topic_name=self.topic,
        )
