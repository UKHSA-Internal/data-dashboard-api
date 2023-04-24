from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.trends.state import Trend

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class TrendsInterface:
    def __init__(
        self,
        topic_name: str,
        metric_name: str,
        percentage_metric_name: str,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.topic_name = topic_name
        self.metric_name = metric_name
        self.percentage_metric_name = percentage_metric_name
        self.core_time_series_manager = core_time_series_manager

    def get_value(self, metric_to_lookup: str) -> float:
        """Gets the value for the record associated with the given `metric_to_lookup`

        Returns:
            float: The associated `metric_value`

        """
        return self.core_time_series_manager.get_latest_metric_value(
            topic=self.topic_name,
            metric_name=metric_to_lookup,
        )

    def create_trend(self) -> Trend:
        """Creates a `Trend` model which represents the trend block.

        Returns:
            `Trend` model with the associated metric values
            and inherent colour and direction calculation logic

        """
        metric_value = self.get_value(metric_to_lookup=self.metric_name)
        percentage_metric_value = self.get_value(
            metric_to_lookup=self.percentage_metric_name
        )

        return Trend(
            metric_name=self.metric_name,
            metric_value=metric_value,
            percentage_metric_name=self.percentage_metric_name,
            percentage_metric_value=percentage_metric_value,
        )
