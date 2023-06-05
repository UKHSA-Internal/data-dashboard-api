from typing import List, Tuple

from django.db.models import Manager, QuerySet

from metrics.data.models import core_models
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.interfaces.charts.access import ChartAxisFields, ChartTypes

DEFAULT_TOPIC_MANAGER = core_models.Topic.objects
DEFAULT_METRIC_MANAGER = core_models.Metric.objects
DEFAULT_STRATUM_MANAGER = core_models.Stratum.objects
DEFAULT_GEOGRAPHY_MANAGER = core_models.Geography.objects
DEFAULT_GEOGRAPHY_TYPE_MANAGER = core_models.GeographyType.objects


class MetricsAPIInterface:
    """This is the explicit interface from which the CMS interacts with the Metrics API from.
    Note that this is enforced via the architectural constraints of this codebase.

    It is intended that the CMS calls for the data that it needs via model managers
    from the Metrics API through this abstraction only.

    Parameters:
    -----------
    topic_manager : `TopicManager`
        The model manager for the `Topic` model belonging to the Metrics API
        Defaults to the concrete `TopicManager` via `Topic.objects`
    metric_manager : `MetricManager`
        The model manager for the `Metric` model belonging to the Metrics API
        Defaults to the concrete `MetricManager` via `Metric.objects`
    stratum_manager : `StratumManager`
        The model manager for the `Stratum` model belonging to the Metrics API
        Defaults to the concrete `StratumManager` via `Stratum.objects`
    geography_manager : `GeographyManager`
        The model manager for the `Geography` model belonging to the Metrics API
        Defaults to the concrete `GeographyManager` via `Geography.objects`
    geography_type_manager : `GeographyTypeManager`
        The model manager for the `GeographyType` model belonging to the Metrics API
        Defaults to the concrete `GeographyTypeManager` via `GeographyType.objects`

    """

    def __init__(
        self,
        topic_manager: Manager = DEFAULT_TOPIC_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
        stratum_manager: Manager = DEFAULT_STRATUM_MANAGER,
        geography_manager: Manager = DEFAULT_GEOGRAPHY_MANAGER,
        geography_type_manager: Manager = DEFAULT_GEOGRAPHY_TYPE_MANAGER,
    ):
        self.topic_manager = topic_manager
        self.metric_manager = metric_manager
        self.stratum_manager = stratum_manager
        self.geography_manager = geography_manager
        self.geography_type_manager = geography_type_manager

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

    @staticmethod
    def get_chart_axis_choices() -> List[Tuple[str, str]]:
        """Gets all available axis choices for a chart as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartAxisFields` enum from the Metrics API

        Returns:
            List[Tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("geography", "geography"), ...]

        """
        return ChartAxisFields.choices()

    @staticmethod
    def get_chart_line_types() -> List[Tuple[str, str]]:
        """Gets all available chart line types choices as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartLineTypes` enum from the Metrics API

        Returns:
            List[Tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("SOLID", "SOLID"), ...]

        """
        return ChartLineTypes.choices()

    @staticmethod
    def get_colours() -> List[Tuple[str, str]]:
        """Gets all available colour choices as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `RGBAChartLineColours` enum from the Metrics API

        Returns:
            List[Tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("BLUE", "BLUE"), ...]

        """
        return RGBAChartLineColours.choices()

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

    def get_all_unique_percent_change_type_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change` & `percent`
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['new_cases_7days_change_percentage', 'new_deaths_7days_change_percentage']>`

        """
        return self.metric_manager.get_all_unique_percent_change_type_names()

    def get_all_stratum_names(self) -> QuerySet:
        """Gets all available stratum names as a flat list queryset.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual stratum names:
                Examples:
                    `<StratumQuerySet ['default', '0_4']>`

        """
        return self.stratum_manager.get_all_names()

    def get_all_geography_names(self) -> QuerySet:
        """Gets all unique geography names as a flat list queryset.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual geography names:
                Examples:
                    `<GeographyQuerySet ['England', 'London']>`
        """
        return self.geography_manager.get_all_names()

    def get_all_geography_type_names(self) -> QuerySet:
        """Gets all available geography_type names as a flat list queryset.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual geography_type names:
                Examples:
                    `<GeographyTypeQuerySet ['Nation', 'UKHSA_Region']>`

        """
        return self.geography_type_manager.get_all_names()
