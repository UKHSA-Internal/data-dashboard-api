from unittest import mock

from cms.metrics_interface import field_choices_callables, interface
from metrics.domain.charts.line_multi_coloured.colour_scheme import RGBAColours
from metrics.domain.charts.line_multi_coloured.properties import ChartLineTypes
from metrics.interfaces.charts.access import ChartTypes


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
        unique_metric_names = field_choices_callables.get_all_unique_metric_names()

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
            field_choices_callables.get_all_unique_change_type_metric_names()
        )

        # Then
        assert unique_change_type_metric_names == [
            (x, x) for x in retrieved_unique_change_type_metric_names
        ]


class TestGetAllUniquePercentChangeTypeMetricNames:
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
            field_choices_callables.get_all_unique_percent_change_type_names()
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
        chart_types = field_choices_callables.get_chart_types()

        # Then
        assert chart_types == retrieved_chart_types


class TestGetChartLineTypes:
    @mock.patch.object(interface.MetricsAPIInterface, "get_chart_line_types")
    def test_delegates_call_correctly(
        self, mocked_get_chart_line_types: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns chart line types
        When `get_chart_line_types()` is called
        Then the chart types are returned as a list of 2-item tuples
        """
        # Given
        retrieved_chart_line_types = ChartLineTypes.choices()
        mocked_get_chart_line_types.return_value = retrieved_chart_line_types

        # When
        chart_line_types = field_choices_callables.get_chart_line_types()

        # Then
        assert chart_line_types == retrieved_chart_line_types


class TestGetColours:
    @mock.patch.object(interface.MetricsAPIInterface, "get_colours")
    def test_delegates_call_correctly(self, mocked_get_colours: mock.MagicMock):
        """
        Given an instance of the `MetricsAPIInterface` which returns available RGBA colours
        When `get_colours()` is called
        Then the colours are returned as a list of 2-item tuples
        """
        # Given
        retrieved_colours = RGBAColours.choices()
        mocked_get_colours.return_value = retrieved_colours

        # When
        colours = field_choices_callables.get_colours()

        # Then
        assert colours == retrieved_colours


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
        topic_names = field_choices_callables.get_all_topic_names()

        # Then
        assert topic_names == [(x, x) for x in retrieved_topic_names]


class TestGetAllStratumNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_stratum_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_stratum_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns stratum names
        When `get_all_stratum_names()` is called
        Then the stratum names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_stratum_names = ["0_4", "5_9"]
        mocked_get_all_stratum_names.return_value = retrieved_stratum_names

        # When
        stratum_names = field_choices_callables.get_all_stratum_names()

        # Then
        assert stratum_names == [(x, x) for x in retrieved_stratum_names]


class TestGetAllGeographyNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_geography_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_geography_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns geography names
        When `get_all_geographies()` is called
        Then the geography names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_geography_names = ["London", "Yorkshire and Humber"]
        mocked_get_all_geography_names.return_value = retrieved_geography_names

        # When
        geographies_names = field_choices_callables.get_all_geography_names()

        # Then
        assert geographies_names == [(x, x) for x in retrieved_geography_names]


class TestGetAllGeographyTypeNames:
    @mock.patch.object(interface.MetricsAPIInterface, "get_all_geography_type_names")
    def test_delegates_call_correctly(
        self, mocked_get_all_geography_type_names: mock.MagicMock
    ):
        """
        Given an instance of the `MetricsAPIInterface` which returns geography type names
        When `get_all_geography_types()` is called
        Then the geography names are returned as a list of 2-item tuples
        """
        # Given
        retrieved_geography_type_names = ["London", "Yorkshire and Humber"]
        mocked_get_all_geography_type_names.return_value = (
            retrieved_geography_type_names
        )

        # When
        geography_type_names = field_choices_callables.get_all_geography_type_names()

        # Then
        assert geography_type_names == [(x, x) for x in retrieved_geography_type_names]
