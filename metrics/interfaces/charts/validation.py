import datetime

from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, Metric

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
        self._validate_series_type_chart_works_with_metric()

    def _validate_series_type_chart_works_with_metric(self) -> None:
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
