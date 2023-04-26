from unittest import mock

from cms.metrics_interface import interface
from metrics.interfaces.charts.access import ChartTypes


class TestMetricsAPIInterface:
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


class TestGetAllUniqueMetricNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_unique_metric_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_metric_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique metric names
        When `get_all_unique_metric_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_metric_names = ["new_cases_daily"]
        mocked_get_all_unique_metric_names.return_value = retrieved_unique_metric_names

        # When
        unique_metric_names = interface.get_all_unique_metric_names()

        # Then
        assert unique_metric_names == [(x, x) for x in retrieved_unique_metric_names]


class TestGetAllUniqueChangeTypeMetricNames:
    @mock.patch.object(
        interface.MetricsAPIInterface, "get_all_unique_change_type_metric_names"
    )
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_change_type_metric_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique metric names
        When `get_all_unique_change_type_metric_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_change_type_metric_names = ["new_cases_daily"]
        mocked_get_all_unique_change_type_metric_names.return_value = (
            retrieved_unique_change_type_metric_names
        )

        # When
        unique_change_type_metric_names = (
            interface.get_all_unique_change_type_metric_names()
        )

        # Then
        assert unique_change_type_metric_names == [
            (x, x) for x in retrieved_unique_change_type_metric_names
        ]


class TestGetAllUniqueChangePercentTypeMetricNames:
    @mock.patch.object(
        interface.MetricsAPIInterface, "get_all_unique_percent_change_type_names"
    )
    def test_delegates_call_correctly(
        self, mocked_get_all_unique_percent_change_type_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns unique metric names
        When `get_all_unique_percent_change_type_names()` is called
        Then the unique metric names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_unique_change_percent_type_metric_names = ["new_cases_daily"]
        mocked_get_all_unique_percent_change_type_names.return_value = (
            retrieved_unique_change_percent_type_metric_names
        )

        # When
        unique_change_percent_type_metric_names = (
            interface.get_all_unique_percent_change_type_names()
        )

        # Then
        assert unique_change_percent_type_metric_names == [
            (x, x) for x in retrieved_unique_change_percent_type_metric_names
        ]


class TestGetChartTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_chart_types")
    def test_delegates_call_correctly(self, mocked_get_chart_types: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns chart types
        When `get_chart_types()` is called
        Then the chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_chart_types = ChartTypes.choices()
        mocked_get_chart_types.return_value = retrieved_chart_types

        # When
        chart_types = interface.get_chart_types()

        # Then
        assert chart_types == retrieved_chart_types


class TestGetAllTopicNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_topic_names")
    def test_delegates_call_correctly(self, mocked_get_all_topic_names: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns topic names
        When `get_all_topic_names()` is called
        Then the topic names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_topic_names = ["COVID-19", "Influenza"]
        mocked_get_all_topic_names.return_value = retrieved_topic_names

        # When
        topic_names = interface.get_all_topic_names()

        # Then
        assert topic_names == [(x, x) for x in retrieved_topic_names]
