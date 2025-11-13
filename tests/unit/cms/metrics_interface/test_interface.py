from unittest import mock

from cms.metrics_interface import interface
from metrics.domain.charts.colour_scheme import RGBAChartLineColours

from metrics.domain.charts.common_charts.plots.line_multi_coloured.properties import (
    ChartLineTypes,
)
from metrics.domain.common.utils import ChartAxisFields, ChartTypes


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
        selectable_chart_types = metrics_api_interface.get_chart_types()

        # Then
        assert selectable_chart_types == ChartTypes.selectable_choices()

    def test_get_headline_chart_type_delegates_call_correctly(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_headline_chart_types()` is called from that object
        Then the call is delegated to the correct method on the `ChartTypes` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        selectable_headline_chart_types = (
            metrics_api_interface.get_headline_chart_types()
        )

        # Then
        assert (
            selectable_headline_chart_types == ChartTypes.selectable_headline_choices()
        )

    def test_get_simplified_chart_type_delegates_calls_correctly(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_simplified_chart_types()` is called from that object
        Then the call is delegated to the correct method on the `ChartTypes` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        selectable_simplified_chart_types = (
            metrics_api_interface.get_simplified_chart_types()
        )

        # Then
        assert (
            selectable_simplified_chart_types
            == ChartTypes.selectable_simplified_chart_choices()
        )

    def test_get_dual_category_chart_types_delegates_call_correctly(self):
        """
        Given an instance of `MetricsAPIInterface`
        When `get_dual_category_chart_types()` is called from that object
        Then the call is delegated to the correct method on the `ChartTypes` enum
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        selectable_dual_category_chart_types = (
            metrics_api_interface.get_dual_category_chart_types()
        )

        # Then
        assert (
            selectable_dual_category_chart_types
            == ChartTypes.dual_category_chart_options()
        )

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
        assert all_chart_types == RGBAChartLineColours.selectable_choices()

    def test_get_all_theme_names_delegates_call_correctly(self):
        """
        Given a `ThemeManager` from the Metrics API app
        When `get_all_theme_names()` is called from that object
        Then the call is delegated to the correct method on the `ThemeManager`
        """
        # Given
        spy_theme_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            theme_manager=spy_theme_manager,
            metric_manager=mock.MagicMock(),
        )

        # When
        all_theme_names = metrics_api_interface.get_all_theme_names()

        # Then
        assert all_theme_names == spy_theme_manager.get_all_names()

    def test_get_all_sub_theme_names_delegates_call_correctly(self):
        """
        Given a `ThemeManager` from the Metrics API app
        When `get_all_theme_names()` is called from that object
        Then the call is delegated to the correct method on the `ThemeManager`
        """
        # Given
        spy_sub_theme_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            sub_theme_manager=spy_sub_theme_manager,
            metric_manager=mock.MagicMock(),
        )

        # When
        all_sub_theme_names = metrics_api_interface.get_all_sub_theme_names()

        # Then
        assert all_sub_theme_names == spy_sub_theme_manager.get_all_names()

    def test_get_all_unique_sub_theme_names_delegates_call_correctly(self):
        """f
        Given a `ThemeManager` from the Metrics API app
        When `get_all_unique_theme_names()` is called from that object
        Then the call is delegated to the correct method on the `ThemeManager`
        """
        # Given
        spy_sub_theme_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            sub_theme_manager=spy_sub_theme_manager,
            metric_manager=mock.MagicMock(),
        )

        # When
        all_unique_sub_theme_names = (
            metrics_api_interface.get_all_unique_sub_theme_names()
        )

        # Then
        assert (
            all_unique_sub_theme_names == spy_sub_theme_manager.get_all_unique_names()
        )

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

    def test_get_all_unique_topic_names_delegates_call_correctly(self):
        """
        Given a `TopicManager` from the Metrics API app
        When `get_all_unique_topic_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `TopicManager`
        """
        # Given
        spy_topic_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            topic_manager=spy_topic_manager,
            metric_manager=mock.Mock(),
        )

        # When
        all_unique_topic_names = metrics_api_interface.get_all_unique_topic_names()

        # Then
        assert (
            all_unique_topic_names
            == spy_topic_manager.get_all_unique_names.return_value
        )

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

    def test_get_all_timeseries_metric_names(self):
        """
        Given a `MetricManager` from the Metrics API app
        When `get_all_timeseries_metric_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method  on the `MetricManager`
        """
        # Given
        spy_metric_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            metric_manager=spy_metric_manager,
            topic_manager=mock.Mock(),
        )

        # When
        all_timeseries_metric_names = (
            metrics_api_interface.get_all_timeseries_metric_names()
        )

        # Then
        assert (
            all_timeseries_metric_names
            == spy_metric_manager.get_all_timeseries_names.return_value
        )

    def test_get_all_headline_metric_names(self):
        """
        Given a `MetricManager` from the Metrics API app
        When `get_all_headline_metric_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method  on the `MetricManager`
        """
        # Given
        spy_metric_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            metric_manager=spy_metric_manager,
            topic_manager=mock.Mock(),
        )

        # When
        all_headline_metric_names = (
            metrics_api_interface.get_all_headline_metric_names()
        )

        # Then
        assert (
            all_headline_metric_names
            == spy_metric_manager.get_all_headline_names.return_value
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

    def test_get_all_geography_names_and_codes_by_geography_type_delegates_calls_correctly(
        self,
    ):
        """
        Given a `GeographyManger` from the metrics API app
        When `get_all_geography_names_and_codes_by_geography_type()` is called from an instance of the
            `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `GeographyManager`
        """
        # Given
        spy_geography_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            geography_manager=spy_geography_manager,
        )

        # When
        geography_names_and_codes = (
            metrics_api_interface.get_all_geography_names_and_codes_by_geography_type(
                geography_type="fake_geography_type_name"
            )
        )

        # Then
        assert (
            geography_names_and_codes
            == spy_geography_manager.get_geography_codes_and_names_by_geography_type.return_value
        )

    def test_get_all_geography_names_by_geography_type_delegates_calls_correctly(
        self,
    ):
        """
        Given a `GeographyManager` from the metrics API app
        When `get_all_geography_names_by_geography_type()` is called from an instance of the
        Then the call is delegated to teh correct method on the `GeographyManager`
        """
        # Given
        spy_geography_manager = mock.Mock()
        metrics_api_interface = interface.MetricsAPIInterface(
            geography_manager=spy_geography_manager,
        )

        # When
        geography_names_by_geography_type = (
            metrics_api_interface.get_all_geography_names_by_geography_type(
                geography_type_name="fake_geography_type_name",
            )
        )

        # Then
        assert (
            geography_names_by_geography_type
            == spy_geography_manager.get_all_geography_names_by_geography_type.return_value
        )

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
        assert all_age_names == spy_age_manager.get_all_names.return_value

    def test_get_geography_code_for_geography_delegates_call_correctly(
        self,
    ):
        """
        Given a `GeographyManager` from the Metrics API app
        When `get_geography_code_for_geography()` is called from an instance of the
        `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `GeographyManager`
        """
        # given
        spy_geography_manager = mock.MagicMock()
        metrics_api_interface = interface.MetricsAPIInterface(
            geography_manager=spy_geography_manager,
        )
        mock_geography = mock.Mock()
        mock_geography_type = mock.Mock()

        # when
        geography_code = metrics_api_interface.get_geography_code_for_geography(
            geography=mock_geography, geography_type=mock_geography_type
        )

        # then
        assert (
            geography_code
            == spy_geography_manager.get_geography_code_for_geography.return_value
        )
        spy_geography_manager.get_geography_code_for_geography.assert_called_once_with(
            geography=mock_geography, geography_type=mock_geography_type
        )
