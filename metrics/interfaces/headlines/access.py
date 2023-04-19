from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects


class HeadlinesInterface:
    def __init__(
        self,
        topic: str,
        metric: str,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.topic = topic
        self.metric = metric
        self.core_time_series_manager = core_time_series_manager

    def get_metric_value(self) -> float:
        """Gets the metric_value for the associated time series record.

        Returns:
            float: The associated `metric_value`

        Raises:
            `MetricIsTimeSeriesTypeError`: If the query returned more than 1 record.
                We expect this if the provided `metric` is for timeseries type data
            `HeadlineNumberDataNotFoundError`: If the query returned no records.

        """
        try:
            return self.core_time_series_manager.get_metric_value(
                topic=self.topic,
                metric_name=self.metric,
            )
        except CoreTimeSeries.MultipleObjectsReturned:
            raise MetricIsTimeSeriesTypeError(
                f"`{self.metric}` is a timeseries-type metric. This should be a headline-type metric"
            )
        except CoreTimeSeries.DoesNotExist:
            raise HeadlineNumberDataNotFoundError(
                "No data could be found for those parameters"
            )


class BaseInvalidHeadlinesRequestError(Exception):
    ...


class MetricIsTimeSeriesTypeError(BaseInvalidHeadlinesRequestError):
    ...


class HeadlineNumberDataNotFoundError(BaseInvalidHeadlinesRequestError):
    ...


def generate_headline_number(topic: str, metric: str):
    """Gets the headline number metric_value for the associated time series record.

    Args:
        topic: The name of the disease being queried.
            E.g. `COVID-19`
        metric: The name of the metric being queried.
            E.g. `new_cases_7days_sum

    Returns:
        float: The associated `metric_value`

    Raises:
        `MetricIsTimeSeriesTypeError`: If the query returned more than 1 record.
            We expect this if the provided `metric` is for timeseries type data
        `HeadlineNumberDataNotFoundError`: If the query returned no records.

    """
    interface = HeadlinesInterface(topic=topic, metric=metric)

    metric_value = interface.get_metric_value()

    return metric_value
