from ingestion.metrics_interface import interface
from metrics.data.enums import TimePeriod
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import (
    Age,
    CoreHeadline,
    CoreTimeSeries,
    Geography,
    GeographyType,
    Metric,
    MetricGroup,
    Stratum,
    SubTheme,
    Theme,
    Topic,
)


class TestMetricsAPIInterface:
    def test_get_theme_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_theme_manager()` is called from that object
        Then the concrete `ThemeManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        theme_manager = metrics_api_interface.get_theme_manager()

        # Then
        assert theme_manager is Theme.objects

    def test_get_sub_theme_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_sub_theme_manager()` is called from that object
        Then the concrete `SubThemeManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        sub_theme_manager = metrics_api_interface.get_sub_theme_manager()

        # Then
        assert sub_theme_manager is SubTheme.objects

    def test_get_topic_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_topic_manager()` is called from that object
        Then the concrete `TopicManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        topic_manager = metrics_api_interface.get_topic_manager()

        # Then
        assert topic_manager is Topic.objects

    def test_get_metric_group_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_metric_group_manager()` is called from that object
        Then the concrete `MetricGroupManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        metric_group_manager = metrics_api_interface.get_metric_group_manager()

        # Then
        assert metric_group_manager is MetricGroup.objects

    def test_get_metric_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_metric_manager()` is called from that object
        Then the concrete `MetricManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        metric_manager = metrics_api_interface.get_metric_manager()

        # Then
        assert metric_manager is Metric.objects

    def test_get_geography_type_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_geography_type_manager()` is called from that object
        Then the concrete `GeographyTypeManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        geography_type_manager = metrics_api_interface.get_geography_type_manager()

        # Then
        assert geography_type_manager is GeographyType.objects

    def test_get_geography_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_geography_manager()` is called from that object
        Then the concrete `GeographyManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        geography_manager = metrics_api_interface.get_geography_manager()

        # Then
        assert geography_manager is Geography.objects

    def test_get_age_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_age_manager()` is called from that object
        Then the concrete `AgeManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        age_manager = metrics_api_interface.get_age_manager()

        # Then
        assert age_manager is Age.objects

    def test_get_stratum_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_stratum_manager()` is called from that object
        Then the concrete `StratumManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        stratum_manager = metrics_api_interface.get_stratum_manager()

        # Then
        assert stratum_manager is Stratum.objects

    def test_get_core_headline_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_core_headline_manager()` is called from that object
        Then the concrete `CoreHeadlineManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        core_headline_manager = metrics_api_interface.get_core_headline_manager()

        # Then
        assert core_headline_manager is CoreHeadline.objects

    def test_get_core_timeseries_manager(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_core_timeseries_manager()` is called from that object
        Then the concrete `CoreTimeSeriesManager` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        core_timseries_manager = metrics_api_interface.get_core_timeseries_manager()

        # Then
        assert core_timseries_manager is CoreTimeSeries.objects

    def test_get_core_headline(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_core_headline()` is called from that object
        Then the concrete `CoreHeadline` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        core_headline = metrics_api_interface.get_core_headline()

        # Then
        assert core_headline is CoreHeadline

    def test_get_core_timeseries(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_core_timeseries()` is called from that object
        Then the concrete `CoreTimeSeries` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        core_time_series = metrics_api_interface.get_core_timeseries()

        # Then
        assert core_time_series is CoreTimeSeries

    def test_get_api_timeseries(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_api_timeseries()` is called from that object
        Then the concrete `APITimeSeries` is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        api_time_series = metrics_api_interface.get_api_timeseries()

        # Then
        assert api_time_series is APITimeSeries

    def test_get_time_period_enum(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_time_period_enum()` is called from that object
        Then the `TimePeriod` enum is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        time_period_enum = metrics_api_interface.get_time_period_enum()

        # Then
        assert time_period_enum is TimePeriod
