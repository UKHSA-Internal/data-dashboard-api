from typing import List

from metrics.data.managers.core_models.metric import MetricManager


class FakeMetricManager(MetricManager):
    """
    A fake version of the `MetricManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, metrics, **kwargs):
        self.metrics = metrics
        super().__init__(**kwargs)

    def get_all_names(self) -> List[str]:
        return [metric.name for metric in self.metrics]
