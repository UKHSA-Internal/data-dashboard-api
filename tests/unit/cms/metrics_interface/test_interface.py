from unittest import mock

from cms.metrics_interface import interface
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.domain.utils import ChartAxisFields, ChartTypes


class TestMetricsAPIInterface:
    def test_get_chart_types_delegates_call_correctly(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_chart_types()` is called from that object
        Then the call is delegated to the correct method on the `ChartTypes` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        all_chart_types = metrics_api_interface.get_chart_types()

        # Then
        assert all_chart_types == ChartTypes.choices()

    def test_get_chart_axis_choices_delegates_call_correctly(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_chart_axis_choices()` is called from that object
        Then the call is delegated to the correct method on the `ChartTypes` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        all_chart_axes = metrics_api_interface.get_chart_axis_choices()

        # Then
        assert all_chart_axes == ChartAxisFields.choices()

    def test_get_chart_line_types_delegates_call_correctly(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_chart_line_types()` is called from that object
        Then the call is delegated to the correct method on the `ChartLineTypes` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        all_chart_types = metrics_api_interface.get_chart_line_types()

        # Then
        assert all_chart_types == ChartLineTypes.choices()

    def test_get_colours_delegates_call_correctly(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_colours()` is called from that object
        Then the call is delegated to the correct method on the `RGBAColours` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        all_chart_types = metrics_api_interface.get_colours()

        # Then
        assert all_chart_types == RGBAChartLineColours.choices()

    def test_get_all_topic_names_delegates_call_correctly(self):
        """
        Given a `TopicManager` from the Metrics API app
        When `get_all_topic_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `TopicManager`
        """
        # Given
        spy_topic_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            topic_manager=spy_topic_manager,
            metric_manager=mock.Mock(),  # stubbed
        )

        # When
        all_topic_names = metrics_api_interface.get_all_topic_names()

        # Then
        assert all_topic_names == spy_topic_manager.get_all_names.return_value

    def test_get_all_unique_metric_names_delegates_call_correctly(self):
        """
        Given a `MetricManager` from the Metrics API app
        When `get_all_unique_metric_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `MetricManager`
        """
        # Given
        spy_metric_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            metric_manager=spy_metric_manager,
            topic_manager=mock.Mock(),  # stubbed
        )

        # When
        all_unique_metric_names = metrics_api_interface.get_all_unique_metric_names()

        # Then
        assert (
            all_unique_metric_names
            == spy_metric_manager.get_all_unique_names.return_value
        )

    def test_get_all_unique_change_type_metric_names_delegates_call_correctly(self):
        """
        Given a `MetricManager` from the Metrics API app
        When `get_all_unique_change_type_metric_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `MetricManager`
        """
        # Given
        spy_metric_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            metric_manager=spy_metric_manager,
            topic_manager=mock.Mock(),  # stubbed
        )

        # When
        all_unique_change_type_metric_names = (
            metrics_api_interface.get_all_unique_change_type_metric_names()
        )

        # Then
        assert (
            all_unique_change_type_metric_names
            == spy_metric_manager.get_all_unique_change_type_names.return_value
        )

    def test_get_all_unique_percent_change_type_names_delegates_call_correctly(
        self,
    ):
        """
        Given a `MetricManager` from the Metrics API app
        When `get_all_unique_percent_change_type_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `MetricManager`
        """
        # Given
        spy_metric_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            metric_manager=spy_metric_manager,
            topic_manager=mock.Mock(),  # stubbed
        )

        # When
        all_unique_percent_change_type_names = (
            metrics_api_interface.get_all_unique_percent_change_type_names()
        )

        # Then
        assert (
            all_unique_percent_change_type_names
            == spy_metric_manager.get_all_unique_percent_change_type_names.return_value
        )

    def test_get_all_stratum_names_delegates_call_correctly(
        self,
    ):
        """
        Given a `StratumManager` from the Metrics API app
        When `get_all_stratum_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `StratumManager`
        """
        # Given
        spy_stratum_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            stratum_manager=spy_stratum_manager,
        )

        # When
        all_stratum_names = metrics_api_interface.get_all_stratum_names()

        # Then
        assert all_stratum_names == spy_stratum_manager.get_all_names.return_value

    def test_get_all_geography_names_delegates_call_correctly(
        self,
    ):
        """
        Given a `GeographyManager` from the Metrics API app
        When `get_all_geography_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `GeographyManager`
        """
        # Given
        spy_geography_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            geography_manager=spy_geography_manager,
        )

        # When
        all_geography_names = metrics_api_interface.get_all_geography_names()

        # Then
        assert all_geography_names == spy_geography_manager.get_all_names.return_value

    def test_get_all_geography_type_names_delegates_call_correctly(
        self,
    ):
        """
        Given a `GeographyTypeManager` from the Metrics API app
        When `get_all_geography_type_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `GeographyTypeManager`
        """
        # Given
        spy_geography_type_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            geography_type_manager=spy_geography_type_manager,
        )

        # When
        all_geography_type_names = metrics_api_interface.get_all_geography_type_names()

        # Then
        assert (
            all_geography_type_names
            == spy_geography_type_manager.get_all_names.return_value
        )

    def test_get_all_sex_names_delegates_call_correctly(self):
        """
        Given a `CoreTimeSeriesManager` from the Metrics API app
        When `get_all_sex_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `CoreTimeSeriesManager`
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        all_sex_names = metrics_api_interface.get_all_sex_names()

        # Then
        assert (
            all_sex_names == spy_core_time_series_manager.get_all_sex_names.return_value
        )

    def test_get_all_age_names_delegates_call_correctly(
        self,
    ):
        """
        Given an `AgeManager` from the Metrics API app
        When `get_all_age_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `AgeManager`
        """
        # Given
        spy_age_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            age_manager=spy_age_manager,
        )

        # When
        all_age_names = metrics_api_interface.get_all_age_names()

        # Then
        assert all_age_names == spy_age_manager.get_all_age_names.return_value

