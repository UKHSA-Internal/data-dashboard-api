from django.db.models import Manager, QuerySet

from metrics.data.models import core_models

DEFAULT_TOPIC_MANAGER = core_models.Topic.objects
DEFAULT_METRIC_MANAGER = core_models.Metric.objects


class MetricsAPIInterface:
    """This is the explicit interface from which the CMS interacts with the Metrics API from.
    Note that this is enforced via the architectural constraints of this codebase.

    It is intended that the CMS calls for the data that it needs via model managers
    from the Metrics API via this abstraction only.

    Parameters:
    -----------
    topic_manager : `TopicManager`
        The model manager for the `Topic` model belonging to the Metrics API
        Defaults to the concrete `TopicManager` via `Topic.objects`
    metric_manager : `MetricManager`
        The model manager for the `Metric` model belonging to the Metrics API
        Defaults to the concrete `MetricManager` via `Metric.objects`
    """

    def __init__(
        self,
        topic_manager: Manager = DEFAULT_TOPIC_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
    ):
        self.topic_manager = topic_manager
        self.metric_manager = metric_manager

    def get_all_topic_names(self) -> QuerySet:
        """Gets all available topic names as a flat list queryset.
        Note this is achieved by delegating the call to the `TopicManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`

        """
        return self.topic_manager.get_all_names()

    def get_all_unique_metric_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_daily', 'new_deaths_daily']>`

        """
        return self.metric_manager.get_all_unique_names()

    def get_all_unique_change_type_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change', 'new_deaths_7days_change']>`

        """
        return self.metric_manager.get_all_unique_change_type_names()

    def get_all_unique_change_percent_type_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change_percentage', 'new_deaths_7days_change_percentage']>`

        """
        return self.metric_manager.get_all_unique_change_percent_type_names()
