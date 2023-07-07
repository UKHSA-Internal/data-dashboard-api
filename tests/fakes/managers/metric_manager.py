from metrics.data.managers.core_models.metric import MetricManager


class FakeMetricManager(MetricManager):
    """
    A fake version of the `MetricManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, metrics, **kwargs):
        self.metrics = metrics
        super().__init__(**kwargs)

    def get_all_names(self) -> list[str]:
        return [metric.name for metric in self.metrics]

    def is_metric_available_for_topic(self, metric_name: str, topic_name: str) -> bool:
        filtered_by_topic = [
            metric
            for metric in self.metrics
            if metric.name == metric_name
            if metric.topic.name == topic_name
        ]

        return bool(filtered_by_topic)

    def get_all_unique_change_type_names(self) -> list[str]:
        unique_metric_names = set(metric.name for metric in self.metrics)
        return [
            metric_name
            for metric_name in unique_metric_names
            if "change" in metric_name
        ]

    def get_all_unique_percent_change_type_names(self) -> list[str]:
        unique_metric_change_type_metric_names = self.get_all_unique_change_type_names()
        return [
            metric_name
            for metric_name in unique_metric_change_type_metric_names
            if "percent" in metric_name
        ]
