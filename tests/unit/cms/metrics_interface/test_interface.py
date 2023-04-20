from unittest import mock

from cms.metrics_interface import MetricsAPIInterface


class TestMetricsAPIInterface:
    def test_get_all_topic_names_delegates_call_correctly(self):
        """
        Given a `TopicManager` from the Metrics API app
        When `get_all_topic_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `TopicManager`
        """
        # Given
        spy_topic_manager = mock.Mock()
        metrics_api_interface = MetricsAPIInterface(
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
        metrics_api_interface = MetricsAPIInterface(
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
        metrics_api_interface = MetricsAPIInterface(
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

    def test_get_all_unique_change_percent_type_metric_names_delegates_call_correctly(
        self,
    ):
        """
        Given a `MetricManager` from the Metrics API app
        When `get_all_unique_change_percent_type_metric_names()` is called from an instance of the `MetricsAPIInterface`
        Then the call is delegated to the correct method on the `MetricManager`
        """
        # Given
        spy_metric_manager = mock.Mock()
        metrics_api_interface = MetricsAPIInterface(
            metric_manager=spy_metric_manager,
            topic_manager=mock.Mock(),  # stubbed
        )

        # When
        all_unique_change_percent_type_metric_names = (
            metrics_api_interface.get_all_unique_change_percent_type_metric_names()
        )

        # Then
        assert (
            all_unique_change_percent_type_metric_names
            == spy_metric_manager.get_all_unique_change_percent_type_names.return_value
        )
