from django.db.models import Manager, QuerySet

from metrics.data.models import core_models
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.common_charts.plots.line_multi_coloured.properties import (
    ChartLineTypes,
)
from metrics.domain.common.utils import ChartAxisFields, ChartTypes

DEFAULT_THEME_MANAGER = core_models.Theme.objects
DEFAULT_SUB_THEME_MANAGER = core_models.SubTheme.objects
DEFAULT_TOPIC_MANAGER = core_models.Topic.objects
DEFAULT_METRIC_MANAGER = core_models.Metric.objects
DEFAULT_STRATUM_MANAGER = core_models.Stratum.objects
DEFAULT_GEOGRAPHY_MANAGER = core_models.Geography.objects
DEFAULT_GEOGRAPHY_TYPE_MANAGER = core_models.GeographyType.objects
DEFAULT_AGE_MANAGER = core_models.Age.objects
DEFAULT_CORE_TIME_SERIES_MANAGER = core_models.CoreTimeSeries.objects
DEFAULT_CORE_HEADLINE_MANAGER = core_models.CoreHeadline.objects


class MetricsAPIInterface:
    """This is the explicit interface from which the CMS interacts with the Metrics API from.
    Note that this is enforced via the architectural constraints of this codebase.

    It is intended that the CMS calls for the data that it needs via model managers
    from the Metrics API through this abstraction only.

    Parameters:
    -----------
    theme_manager : `ThemeManager`
        The model manager for the `Theme` model belonging to the Metrics API
        Defaults to the concrete `ThemeManager` via `Theme.objects`
    sub_theme_manager : `SubThemeManager`
        The model manager for the `SubTheme` model belonging to the Metrics API
        Defaults to the concrete `SubThemeManager` via `SubTheme.objects`
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
    age_manager : `AgeManager`
        The model manager for the `Age` model belonging to the Metrics API
        Defaults to the concrete `AgeManager` via `Age.objects`
    core_time_series_manager : `CoreTimeSeriesManager`
        The model manager for the `CoreTimeSeries` model belonging to the Metrics API
        Defaults to the concrete `CoreTimeSeriesManager` via `CoreTimeSeries.objects`
    core_headline_manager : `CoreHeadlineManager`
        The model manager for the `CoreHeadline` model belonging to the Metrics API
        Defaults to the concrete `CoreHeadlineManager` via `CoreHeadline.objects`

    """

    def __init__(
        self,
        *,
        theme_manager: Manager = DEFAULT_THEME_MANAGER,
        sub_theme_manager: Manager = DEFAULT_SUB_THEME_MANAGER,
        topic_manager: Manager = DEFAULT_TOPIC_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
        stratum_manager: Manager = DEFAULT_STRATUM_MANAGER,
        geography_manager: Manager = DEFAULT_GEOGRAPHY_MANAGER,
        geography_type_manager: Manager = DEFAULT_GEOGRAPHY_TYPE_MANAGER,
        age_manager: Manager = DEFAULT_AGE_MANAGER,
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        self.theme_manager = theme_manager
        self.sub_theme_manager = sub_theme_manager
        self.topic_manager = topic_manager
        self.metric_manager = metric_manager
        self.stratum_manager = stratum_manager
        self.geography_manager = geography_manager
        self.geography_type_manager = geography_type_manager
        self.age_manager = age_manager
        self.core_time_series_manager = core_time_series_manager
        self.core_headline_manager = core_headline_manager

    @staticmethod
    def get_chart_types() -> tuple[tuple[str, str], ...]:
        """Gets all available chart type choices as a nested tuple of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartTypes` enum from the Metrics API

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("line_with_shaded_section", "line_with_shaded_section"), ...)

        """
        return ChartTypes.selectable_choices()

    @staticmethod
    def get_headline_chart_types() -> tuple[tuple[str, str], ...]:
        """Gets all available chart type choices for headline charts as a nested tuple of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartTypes` enum from the Metrics API

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("bar", "bar"), ...)

        """
        return ChartTypes.selectable_headline_choices()

    @staticmethod
    def get_simplified_chart_types() -> tuple[tuple[str, str], ...]:
        """Gets all available chart type choices for headline charts as a nested tuple of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartTypes` enum from the metrics API

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("line_single_simplified", "line_single_simplified"), ...)
        """
        return ChartTypes.selectable_simplified_chart_choices()

    @staticmethod
    def get_dual_category_chart_types() -> tuple[tuple[str, str], ...]:
        """Gets all available chart type choices for dual category charts as a nested tuple of 2-item tuples.
        Note this is achieved by delegating the calle to the `ChartTypes` enum from the Metrics API

        Returns:
            Nested tuples of 2 item tuples as expected by the form blocks.
            Examples:
                (("stacked_bar", "stacked_bar"), ...)
        """
        return ChartTypes.dual_category_chart_options()

    @staticmethod
    def get_chart_axis_choices() -> list[tuple[str, str]]:
        """Gets all available axis choices for a chart as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartAxisFields` enum from the Metrics API

        Returns:
            list[tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("geography", "geography"), ...]

        """
        return ChartAxisFields.choices()

    @staticmethod
    def get_chart_line_types() -> list[tuple[str, str]]:
        """Gets all available chart line types choices as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `ChartLineTypes` enum from the Metrics API

        Returns:
            list[tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("SOLID", "SOLID"), ...]

        """
        return ChartLineTypes.choices()

    @staticmethod
    def get_colours() -> list[tuple[str, str]]:
        """Gets all available colour choices as a list of 2-item tuples.
        Note this is achieved by delegating the call to the `RGBAChartLineColours` enum from the Metrics API

        Returns:
            list[tuple[str, str]]: List of 2 item tuples as expected by the form blocks.
            Examples:
                [("BLUE", "BLUE"), ...]

        """
        return RGBAChartLineColours.selectable_choices()

    def get_all_theme_names(self) -> QuerySet:
        """Gets all available theme names as a flat list queryset.
        Note this is achieved by delegating the call to the `ThemeManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual theme names.
                Examples:
                    `<ThemeQuerySet ['infectious_disease', ...]>`.
        """
        return self.theme_manager.get_all_names()

    def get_all_sub_theme_names(self) -> QuerySet:
        """Gets all available sub_theme names as a flat list queryset.
        Note this is achieved by delegating the call to the `SubThemeManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual sub_theme names.
                Examples:
                    `<SubThemeQuerySet ['respiratory', ...]>
        """
        return self.sub_theme_manager.get_all_names()

    def get_all_unique_sub_theme_names(self) -> QuerySet:
        """Get all unique sub_theme names as a flat list queryset.
        Note this is achieved by delegating the call to the `SubThemeManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual sub_theme names.
                Examples:
                    `<SubThemeQuerySet ['respiratory', ...]>

        """
        return self.sub_theme_manager.get_all_unique_names()

    def get_all_topic_names(self) -> QuerySet:
        """Gets all available topic names as a flat list queryset.
        Note this is achieved by delegating the call to the `TopicManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`

        """
        return self.topic_manager.get_all_names()

    def get_all_unique_topic_names(self) -> QuerySet:
        """Get all unique topic names as a flat list queryset.
        Note this is achieved by delegating the call to the `TopicManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`
        """
        return self.topic_manager.get_all_unique_names()

    def get_all_unique_metric_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_deaths_ONSByDay']>`

        """
        return self.metric_manager.get_all_unique_names()

    def get_all_timeseries_metric_names(self) -> QuerySet:
        """Gets all unique metric names that belong to a timeseries metric_group as a flat list.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_deaths_ONSByDay', 'COVID-19_deaths_ONSByDay']>`

        """
        return self.metric_manager.get_all_timeseries_names()

    def get_all_headline_metric_names(self) -> QuerySet:
        """Get all unique metric names that belong to a headline `metric_group` as flat list.
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet ['COVID-19_headline_cases_7DayTotals', 'COVID-19_headline_ONSdeaths_7DayChange']>`
        """
        return self.metric_manager.get_all_headline_names()

    def get_all_unique_change_type_metric_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change`
        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet [
                        'COVID-19_headline_ONSdeaths_7DayChange',
                        'COVID-19_headline_ONSdeaths_7DayChange'
                        ]>`

        """
        return self.metric_manager.get_all_unique_change_type_names()

    def get_all_unique_percent_change_type_names(self) -> QuerySet:
        """Gets all unique metric names as a flat list queryset, which contain the word `change` & `percent`

        Note this is achieved by delegating the call to the `MetricManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual metric names without repetition:
                Examples:
                    `<MetricQuerySet [
                        'COVID-19_headline_ONSdeaths_7DayPercentChange',
                        'COVID-19_headline_ONSdeaths_7DayPercentChange'
                        ]>`

        """
        return self.metric_manager.get_all_unique_percent_change_type_names()

    def get_all_stratum_names(self) -> QuerySet:
        """Gets all available stratum names as a flat list queryset.
        Note this is achieved by delegating the call to the `StratumManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual stratum names:
                Examples:
                    `<StratumQuerySet ['default']>`

        """
        return self.stratum_manager.get_all_names()

    def get_all_geography_names(self) -> QuerySet:
        """Gets all unique geography names as a flat list queryset.
        Note this is achieved by delegating the call to the `GeographyManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual geography names:
                Examples:
                    `<GeographyQuerySet ['England', 'London']>`
        """
        return self.geography_manager.get_all_names()

    def get_all_geography_names_and_codes_by_geography_type(
        self, geography_type: str
    ) -> QuerySet:
        """Gets all geography names and codes for a particular geography type, for example `Nation` or
            `Government Office Region`.
        Note this is achived by delegating the call to the `GeographyManager` from Metrics API

        Returns
            QuerySet: A queryset of the geography_code and geography_names fields as a list of tuples.
                Example:
                    `<GeographyQuerySet [('North East', 'E06000001'), ('North West', 'E06000002')]>`

        """
        return self.geography_manager.get_geography_codes_and_names_by_geography_type(
            geography_type_name=geography_type,
        )

    def get_all_geography_names_by_geography_type(
        self,
        geography_type_name: str,
    ):
        """Gets all geography names for a particular geography type, for example `Nation` or
            `Government Office Region`.

        Note: this is achieved by delegating the call to the `GeographyManager` from Metrics API

        Returns:
            QuerySet: A queryset of the geography_names fields as a list of tuples.
                Example:
                    `<GeographyQuerySet ['North East', 'North West']>`
        """
        return self.geography_manager.get_all_geography_names_by_geography_type(
            geography_type_name=geography_type_name,
        )

    def get_all_geography_type_names(self) -> QuerySet:
        """Gets all available geography_type names as a flat list queryset.
        Note this is achieved by delegating the call to the `GeographyTypeManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual geography_type names:
                Examples:
                    `<GeographyTypeQuerySet ['Nation', 'UKHSA_Region']>`

        """
        return self.geography_type_manager.get_all_names()

    def get_all_age_names(self) -> QuerySet:
        """Gets all available age names as a flat list queryset.

        Note this is achieved by delegating the call to the `AgeManager` from the Metrics API

        Returns:
            QuerySet: A queryset of the individual age names:
                Examples:
                    `<AgeQuerySet ['40-44', '45-54']>`

        """
        return self.age_manager.get_all_names()
