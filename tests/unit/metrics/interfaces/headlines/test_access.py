from unittest import mock

import pytest

from metrics.data.managers.core_models.headline import CoreHeadlineManager
from metrics.data.models.core_models import CoreHeadline
from metrics.domain.headlines.state import Headline
from metrics.interfaces.headlines import access

EXPECTED_DATE_FORMAT = "%Y-%m-%d"


@pytest.fixture
def example_headline_args() -> dict[str, str]:
    return {
        "topic_name": "COVID-19",
        "metric_name": "COVID-19_headline_ONSdeaths_7DayChange",
        "geography_name": "England",
        "geography_type_name": "Nation",
        "stratum_name": "default",
        "age": "all",
        "sex": "all",
    }


class TestHeadlinesInterface:
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
        headlines_interface = access.HeadlinesInterface(**example_args)

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
        mocked_core_headline = mock.Mock(metric_value=123, period_end="2024-02-29")
        spy_core_headline_manager = mock.Mock()
        spy_core_headline_manager.get_latest_headline.return_value = (
            mocked_core_headline
        )

        headlines_interface = access.HeadlinesInterface(
            **expected_example_args,
            core_headline_manager=spy_core_headline_manager,
        )

        # When
        headline: Headline = headlines_interface.get_latest_metric_value()

        # Then
        assert headline.metric_value == mocked_core_headline.metric_value
        assert (
            headline.period_end.strftime(EXPECTED_DATE_FORMAT)
            == mocked_core_headline.period_end
        )

        spy_core_headline_manager.get_latest_headline.assert_called_once_with(
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
        spy_core_headline_manager.get_latest_headline.return_value = None

        headlines_interface = access.HeadlinesInterface(
            **expected_example_args,
            core_headline_manager=spy_core_headline_manager,
        )

        # When / Then
        with pytest.raises(access.HeadlineNumberDataNotFoundError):
            headlines_interface.get_latest_metric_value()


class TestGenerateHeadlineNumber:
    @mock.patch.object(access.HeadlinesInterface, "get_latest_metric_value")
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
        metric_value = access.generate_headline_number(**example_args)

        # Then
        assert metric_value == spy_get_latest_metric_value.return_value

    @mock.patch.object(CoreHeadlineManager, "get_latest_headline")
    def test_raises_error_when_metric_value_is_none(
        self,
        mocked_get_latest_headline: mock.MagicMock,
        example_headline_args: dict[str, str],
    ):
        """
        Given a set of fake arguments for a record which does not exist
        When `generate_headline_number()` is called
        Then a `HeadlineNumberDataNotFoundError` is raised
        """
        # Given
        example_args = example_headline_args
        mocked_get_latest_headline.return_value = None

        # When / Then
        with pytest.raises(access.HeadlineNumberDataNotFoundError):
            access.generate_headline_number(**example_args)
