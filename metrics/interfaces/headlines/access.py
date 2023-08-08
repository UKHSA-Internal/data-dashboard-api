from django.db.models import Manager

from metrics.data.models.core_models import CoreTimeSeries, CoreHeadline

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class HeadlinesInterface:
    def __init__(
        self,
        topic_name: str,
        metric_name: str,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        self.topic_name = topic_name
        self.metric_name = metric_name
        self.core_time_series_manager = core_time_series_manager
        self.core_headline_manager = core_headline_manager

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
                topic_name=self.topic_name,
                metric_name=self.metric_name,
            )
        except CoreTimeSeries.MultipleObjectsReturned:
            raise MetricIsTimeSeriesTypeError(
                f"`{self.metric_name}` is a timeseries-type metric. This should be a headline-type metric"
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


def generate_headline_number(topic_name: str, metric_name: str) -> float:
    """Gets the headline number metric_value for the associated time series record.

    Args:
        topic_name: The name of the disease being queried.
            E.g. `COVID-19`
        metric_name: The name of the metric being queried.
            E.g. `COVID-19_headline_ONSdeaths_7daytotals`

    Returns:
        float: The associated `metric_value`

    Raises:
        `MetricIsTimeSeriesTypeError`: If the query returned more than 1 record.
            We expect this if the provided `metric` is for timeseries type data
        `HeadlineNumberDataNotFoundError`: If the query returned no records.

    """
    interface = HeadlinesInterface(topic_name=topic_name, metric_name=metric_name)

    metric_value = interface.get_metric_value()

    return metric_value
