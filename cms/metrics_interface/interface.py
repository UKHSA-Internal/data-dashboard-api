from typing import List, Tuple

from django.db.models import Manager, QuerySet

from metrics.data.models import core_models
from metrics.interfaces.charts.access import ChartTypes

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

    @staticmethod
    def get_chart_types() -> List[Tuple[str, str]]:
        """Gets all available chart type choices as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartTypes` enum from the Metrics API

        Returns:
            List[Tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("line_with_shaded_section", "line_with_shaded_section"), ...]

        """
        return ChartTypes.choices()

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

    def get_all_unique_change_type_metric_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change', 'new_deaths_7days_change']>`

        """
        return self.metric_manager.get_all_unique_change_type_names()

    def get_all_unique_change_percent_type_metric_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change` & `percent`
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change_percentage', 'new_deaths_7days_change_percentage']>`

        """
        return self.metric_manager.get_all_unique_change_percent_type_names()


def _build_two_item_tuple_choices(choices: List[str]) -> List[Tuple[str, str]]:
    return [(choice, choice) for choice in choices]


def get_all_unique_metric_names():
    """Callable for the `choices` on the `metric` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Metric` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of unique metric names.
        Examples:
            [("new_cases_daily", "new_cases_daily"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_unique_metric_names()
    )


def get_chart_types() -> List[Tuple[str, str]]:
    """Callable for the `choices` on the `chart_type` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new chart type is added.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of chart_types.
        Examples:
            [("line_with_shaded_section", "line_with_shaded_section"), ...]

    """
    return MetricsAPIInterface.get_chart_types()


def get_all_topic_names():
    """Callable for the `choices` on the `topic` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Topic` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of topic names.
        Examples:
            [("COVID-19", "COVID-19"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(metrics_interface.get_all_topic_names())


def get_all_unique_change_type_metric_names():
    """Callable for the `choices` on the `metric` fields of trend number CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Metric` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of change type metric names.
        Examples:
            [("new_cases_7days_change", "new_cases_7days_change"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_unique_change_type_metric_names()
    )


def get_all_unique_change_percent_type_metric_names():
    """Callable for the `choices` on the `percentage_metric` fields of the CMS blocks.

    Notes:
        This callable wraps the `MetricsAPIInterface`
        and is passed to a migration for the CMS blocks.
        This means that we don't need to create a new migration
        whenever a new `Metric` is added to that table.
        Instead, the 1-off migration is pointed at this callable.
        So Wagtail will pull the choices by invoking this function.

    Returns:
        A list of 2-item tuples of change percent type metric names.
        Examples:
            [("new_cases_7days_change_percentage", "new_cases_7days_change_percentage"), ...]

    """
    metrics_interface = MetricsAPIInterface()
    return _build_two_item_tuple_choices(
        metrics_interface.get_all_unique_change_percent_type_metric_names()
    )
