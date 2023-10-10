from django.core.exceptions import ObjectDoesNotExist

from metrics.data.managers.core_models.metric import MetricManager
from tests.fakes.models.metrics.metric import FakeMetric


class FakeMetricManager(MetricManager):
    """
    A fake version of the `MetricManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, metrics, **kwargs):
        self.metrics = metrics
        super().__init__(**kwargs)

    def get(self, **kwargs):
        metrics = self.metrics
        for field, value in kwargs.items():
            metrics = [x for x in metrics if getattr(x, field) == value]

        try:
            return metrics[0]
        except IndexError:
            raise ObjectDoesNotExist

    def get_or_create(self, defaults=None, **kwargs) -> tuple[FakeMetric, bool]:
        try:
            return self.get(**kwargs), False
        except ObjectDoesNotExist:
            created_metric = FakeMetric(**kwargs)
            self.metrics.append(created_metric)
            return created_metric, True

    def get_all_names(self) -> list[str]:
        return [metric.name for metric in self.metrics]

    def get_all_headline_names(self) -> list[str]:
        return [
            metric.name
            for metric in self.metrics
            if metric.metric_group.name == "headline"
        ]

    def is_metric_available_for_topic(self, metric_name: str, topic_name: str) -> bool:
        filtered_by_topic = [
            metric
            for metric in self.metrics
            if metric.name == metric_name
            if metric.topic.name == topic_name
        ]

        return bool(filtered_by_topic)

    def get_all_unique_change_type_names(self) -> list[str]:
        unique_metric_names = {metric.name for metric in self.metrics}
        return [
            metric_name
            for metric_name in unique_metric_names
            if "change" in metric_name.lower()
        ]

    def get_all_unique_percent_change_type_names(self) -> list[str]:
        unique_metric_change_type_metric_names = self.get_all_unique_change_type_names()
        return [
            metric_name
            for metric_name in unique_metric_change_type_metric_names
            if "Percent" in metric_name
        ]
