from decimal import Decimal
from unittest import mock

import pytest

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.interfaces.headlines import access


@pytest.fixture
def example_headline_args() -> dict[str, str]:
    return {
        "topic_name": "COVID-19",
        "metric_name": "COVID-19_headline_ONSdeaths_7daychange",
        "geography_name": "England",
        "geography_type_name": "Nation",
        "stratum_name": "default",
        "age": "all",
        "sex": "all",
    }


class TestHeadlinesInterface:
    def test_initializes_with_default_manager(self):
        """
        Given a mocked topic and metric
        When an instance of the `HeadlinesInterface` is created
        Then the default `CoreHeadlineManager`
            is set on the `HeadlinesInterface` object
        """
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()

        # When
        headlines_interface = access.HeadlinesInterface(
            topic_name=mocked_topic,
            metric_name=mocked_metric,
        )

        # Then
        assert headlines_interface.core_headline_manager == CoreHeadline.objects

    def test_get_metric_value_calls_core_time_series_manager_with_correct_args(self):
        """
        Given a `CoreTimeSeriesManager`
        When `get_metric_value()` is called from an instance of `HeadlinesInterface`
        Then the correct method is called from `CoreTimeSeriesManager` to retrieve the metric_value
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        headlines_interface = access.HeadlinesInterface(
            topic_name=mocked_topic,
            metric_name=mocked_metric,
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When
        metric_value: Decimal = headlines_interface.get_metric_value()

        # Then
        assert (
            metric_value == spy_core_time_series_manager.get_metric_value.return_value
        )
        spy_core_time_series_manager.get_metric_value.assert_called_once_with(
            topic_name=mocked_topic,
            metric_name=mocked_metric,
        )

    def test_get_metric_value_raises_error_when_model_manager_raises_error_for_timeseries_type_data(
        self,
    ):
        """
        Given a `CoreTimeSeriesManager` which raises a `MultipleObjectsReturned` error when called
        When `get_metric_value()` is called from an instance of `HeadlinesInterface`
        Then the underlying error is caught and a `MetricIsTimeSeriesTypeError` is raised
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        spy_core_time_series_manager.get_metric_value.side_effect = [
            CoreTimeSeries.MultipleObjectsReturned
        ]
        fake_metric_name = "COVID-19"

        headlines_interface = access.HeadlinesInterface(
            topic_name=mock.Mock(),
            metric_name=fake_metric_name,
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When / Then
        expected_error_message = f"`{fake_metric_name}` is a timeseries-type metric. This should be a headline-type metric"
        with pytest.raises(
            access.MetricIsTimeSeriesTypeError, match=expected_error_message
        ):
            headlines_interface.get_metric_value()

    def test_get_metric_value_raises_error_when_model_manager_raises_error_for_no_data_found(
        self,
    ):
        """
        Given a `CoreTimeSeriesManager` which raises a `DoesNotExist` error when called
        When `get_metric_value()` is called from an instance of `HeadlinesInterface`
        Then the underlying error is caught and a `HeadlineNumberDataNotFoundError` is raised
        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        spy_core_time_series_manager.get_metric_value.side_effect = [
            CoreTimeSeries.DoesNotExist
        ]

        headlines_interface = access.HeadlinesInterface(
            topic_name=mock.Mock(),
            metric_name=mock.Mock(),
            core_time_series_manager=spy_core_time_series_manager,
        )

        # When / Then
        expected_error_message = "No data could be found for those parameters"
        with pytest.raises(
            access.HeadlineNumberDataNotFoundError, match=expected_error_message
        ):
            headlines_interface.get_metric_value()


class TestHeadlinesInterfaceBeta:
    def test_initializes_with_default_manager(
        self, example_headline_args: dict[str, str]
    ):
        """
        Given a set of fake arguments
        When an instance of the `HeadlinesInterface` is created
        Then the default `CoreHeadlineManager`
            is set on the `HeadlinesInterface` object
        """
        # Given
        example_args = example_headline_args

        # When
        headlines_interface = access.HeadlinesInterfaceBeta(**example_args)

        # Then
        assert headlines_interface.core_headline_manager == CoreHeadline.objects

    def test_get_metric_value_calls_core_time_series_manager_with_correct_args(
        self, example_headline_args: dict[str, str]
    ):
        """
        Given a `CoreTimeSeriesManager`
        When `get_latest_metric_value()`
            is called from an instance of `HeadlinesInterface`
        Then the correct method is called from `CoreHeadlineManager`
            to retrieve the latest metric_value
        """
        # Given
        expected_example_args = example_headline_args

        spy_core_headline_manager = mock.Mock()
        headlines_interface = access.HeadlinesInterfaceBeta(
            **expected_example_args,
            core_headline_manager=spy_core_headline_manager,
        )

        # When
        metric_value: Decimal = headlines_interface.get_latest_metric_value()

        # Then
        assert (
            metric_value
            == spy_core_headline_manager.get_latest_metric_value.return_value
        )
        spy_core_headline_manager.get_latest_metric_value.assert_called_once_with(
            **expected_example_args,
        )

    def test_get_metric_value_raises_error_when_model_manager_raises_error_for_no_data_found(
        self, example_headline_args: dict[str, str]
    ):
        """
        Given a `CoreHeadlineManager` which contains no matching `CoreHeadline` objects
        When `get_latest_metric_value()`
            is called from an instance of `HeadlinesInterface`
        Then a `HeadlineNumberDataNotFoundError` is raised
        """
        # Given
        expected_example_args = example_headline_args
        spy_core_headline_manager = mock.Mock()
        spy_core_headline_manager.get_latest_metric_value.return_value = None

        headlines_interface = access.HeadlinesInterfaceBeta(
            **expected_example_args,
            core_headline_manager=spy_core_headline_manager,
        )

        # When / Then
        metric_name = expected_example_args["metric_name"]
        topic_name = expected_example_args["topic_name"]
        expected_error_message = (
            f"Data for `{topic_name}` and `{metric_name}` could not be found."
        )
        with pytest.raises(
            access.HeadlineNumberDataNotFoundError, match=expected_error_message
        ):
            headlines_interface.get_latest_metric_value()


class TestGenerateHeadlineNumber:
    @mock.patch.object(access.HeadlinesInterface, "get_metric_value")
    def test_delegates_call_to_interface_to_get_metric_value(
        self, spy_get_metric_value: mock.MagicMock
    ):
        """
        Given a topic and metric
        When `generate_headline_number()` is called
        Then the call is delegated to `get_metric_value()` from an instance of the `HeadlinesInterface`
        """
        # Given
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()

        # When
        metric_value = access.generate_headline_number(
            topic_name=mocked_topic,
            metric_name=mocked_metric,
        )

        # Then
        assert metric_value == spy_get_metric_value.return_value

    @mock.patch.object(access.HeadlinesInterface, "get_metric_value")
    def test_raises_error_when_metric_value_is_none(
        self, mocked_get_metric_value: mock.MagicMock
    ):
        """
        Given a topic and metric which do not exist
        When `generate_headline_number()` is called
        Then a `HeadlineNumberDataNotFoundError` is raised
        """
        # Given
        mocked_topic = mock.Mock()
        mocked_metric = mock.Mock()
        mocked_get_metric_value.return_value = None

        # When / Then
        with pytest.raises(HeadlineNumberDataNotFoundError):
            access.generate_headline_number(
                topic_name=mocked_topic,
                metric_name=mocked_metric,
            )


class TestGenerateHeadlineNumberBeta:
    @mock.patch.object(access.HeadlinesInterfaceBeta, "get_latest_metric_value")
    def test_delegates_call_to_interface_to_get_latest_metric_value(
        self,
        spy_get_latest_metric_value: mock.MagicMock,
        example_headline_args: dict[str, str],
    ):
        """
        Given a set of fake arguments
        When `generate_headline_number()` is called
        Then the call is delegated to `get_latest_metric_value()`
            from an instance of the `HeadlinesInterface`
        """
        # Given
        example_args = example_headline_args

        # When
        metric_value = access.generate_headline_number_beta(**example_args)

        # Then
        assert metric_value == spy_get_latest_metric_value.return_value

    @mock.patch.object(access.HeadlinesInterfaceBeta, "get_latest_metric_value")
    def test_raises_error_when_metric_value_is_none(
        self,
        mocked_get_metric_value: mock.MagicMock,
        example_headline_args: dict[str, str],
    ):
        """
        Given a set of fake arguments for a record which does not exist
        When `generate_headline_number()` is called
        Then a `HeadlineNumberDataNotFoundError` is raised
        """
        # Given
        example_args = example_headline_args
        mocked_get_metric_value.return_value = None

        # When / Then
        with pytest.raises(access.HeadlineNumberDataNotFoundError):
            access.generate_headline_number_beta(**example_args)
