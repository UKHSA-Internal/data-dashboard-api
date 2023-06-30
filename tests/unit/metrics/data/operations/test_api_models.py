from unittest import mock

import _pytest
import pytest

from metrics.data.managers.api_models.time_series import APITimeSeriesManager
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries
from metrics.data.operations.api_models import (
    create_api_time_series_from_core_time_series,
    generate_api_time_series,
)
from tests.fakes.factories.metrics.api_time_series_factory import (
    FakeAPITimeSeriesFactory,
)
from tests.fakes.managers.api_time_series_manager import FakeAPITimeSeriesManager
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager

MODULE_PATH: str = "metrics.data.operations.api_models"


@pytest.fixture
def mocked_empty_api_time_series_manager() -> mock.Mock:
    mocked_manager = mock.Mock(spec_set=APITimeSeriesManager)
    # If there are existing API time series records
    # Then `generate_api_time_series()` returns early
    mocked_manager.exists.return_value = False
    return mocked_manager


class TestGenerateAPITimeSeries:
    @mock.patch(f"{MODULE_PATH}.create_api_time_series_from_core_time_series")
    def test_calls_bulk_create_on_all_api_time_series(
        self,
        mocked_create_api_time_series_from_core_time_series: mock.MagicMock,
        mocked_empty_api_time_series_manager,
    ):
        """
        Given a `APITimeManager` and a `FakeTimeSeriesManager`.
        When `generate_api_time_series()` is called.
        Then `bulk_create()` is called from the `APITimeManager` with the correct args.

        Patches:
          `mocked_create_api_time_series_from_core_time_series`: Isolation of the
                return values to be passed to the main assertion.
        """
        # Given
        spy_api_time_series_manager = mocked_empty_api_time_series_manager

        mocked_time_series = [
            mock.Mock(spec=CoreTimeSeries),
            mock.Mock(spec=CoreTimeSeries),
        ]

        # When
        generate_api_time_series(
            core_time_series_manager=FakeCoreTimeSeriesManager(
                time_series=mocked_time_series
            ),
            api_time_series_manager=spy_api_time_series_manager,
        )

        # Then
        expected_created_api_time_series = [
            mocked_create_api_time_series_from_core_time_series.return_value
        ] * 2
        spy_api_time_series_manager.bulk_create.assert_called_once_with(
            objs=expected_created_api_time_series,
            batch_size=100,
        )

    @mock.patch(f"{MODULE_PATH}.create_api_time_series_from_core_time_series")
    def test_calls_create_api_time_series_from_core_time_series_on_filtered_time_series(
        self,
        spy_create_api_time_series_from_core_time_series: mock.MagicMock,
        mocked_empty_api_time_series_manager,
    ):
        """
        Given a `TimeSeriesManager` and a mocked `TimeSeries` object
        When `generate_weekly_time_series()` is called.
        Then `create_api_time_series_from_core_time_series()` with the correct args.
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)
        mocked_time_series_manager = mock.Mock()
        mocked_time_series_manager.all_related.return_value = [mocked_time_series]

        # When
        generate_api_time_series(
            core_time_series_manager=mocked_time_series_manager,
            api_time_series_manager=mocked_empty_api_time_series_manager,  # stubbed
        )

        # Then
        assert spy_create_api_time_series_from_core_time_series.mock_calls == [
            mock.call(core_time_series=mocked_time_series)
        ]

    @mock.patch(f"{MODULE_PATH}.create_api_time_series_from_core_time_series")
    def test_returns_early_if_api_time_series_already_exist(
        self, spy_create_api_time_series_from_core_time_series: mock.MagicMock
    ):
        """
        Given an `APITimeSeriesManager` which returns True when `exists()` is called
        When `generate_api_time_series()` is called
        Then the function returns early

        Patches:
            `spy_create_api_time_series_from_core_time_series`: For the main assertion.

        """
        # Given
        spy_core_time_series_manager = mock.Mock()
        fake_api_time_series = (
            FakeAPITimeSeriesFactory.build_example_api_time_series_fields_missing()
        )
        fake_api_time_series_manager = FakeAPITimeSeriesManager(
            time_series=[fake_api_time_series]
        )

        # When
        generate_api_time_series(
            core_time_series_manager=spy_core_time_series_manager,
            api_time_series_manager=fake_api_time_series_manager,
        )

        # Then
        spy_core_time_series_manager.all_related.assert_not_called()
        spy_create_api_time_series_from_core_time_series.assert_not_called()

    def test_log_statement_recorded_when_returning_early(
        self, caplog: _pytest.logging.LogCaptureFixture
    ):
        """
        Given an `APITimeSeriesManager` which returns True when `exists()` is called
        When `generate_api_time_series()` is called
        Then the expected log statement is recorded

        """
        # Given
        fake_api_time_series_manager = FakeAPITimeSeriesManager(
            time_series=[FakeAPITimeSeriesFactory.build_example_covid_time_series()]
        )

        # When
        generate_api_time_series(
            api_time_series_manager=fake_api_time_series_manager,
        )

        # Then
        assert "API Time Series table has existing records" in caplog.text

    def test_bulk_create_not_called_on_api_time_series_manager_when_returning_early(
        self,
    ):
        """
        Given an `APITimeSeriesManager` which returns True when `exists()` is called
        When `generate_api_time_series()` is called
        Then the `bulk_create()` method will not be called

        """
        # Given
        spy_api_time_series_manager = mock.Mock()
        spy_api_time_series_manager.exists.return_value = True

        # When
        generate_api_time_series(
            api_time_series_manager=spy_api_time_series_manager,
        )

        # Then
        spy_api_time_series_manager.bulk_create.assert_not_called()


class TestCreateAPITimeSeriesFromCoreTimeSeries:
    def test_uses_correct_fields_from_core_time_series(self):
        """
        Given a mocked `TimeSeries` object
        When `api_time_series()` is called
        Then an `APITimeSeries` object is created
        And it takes the correct fields from the `TimeSeries` object
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)

        # When
        api_time_series = create_api_time_series_from_core_time_series(
            core_time_series=mocked_time_series
        )

        # Then
        assert isinstance(api_time_series, APITimeSeries)
        assert api_time_series.period == mocked_time_series.period
        assert (
            api_time_series.theme
            == mocked_time_series.metric.topic.sub_theme.theme.name
        )
        assert (
            api_time_series.sub_theme == mocked_time_series.metric.topic.sub_theme.name
        )
        assert api_time_series.topic == mocked_time_series.metric.topic.name
        assert api_time_series.geography == mocked_time_series.geography.name
        assert (
            api_time_series.geography_type
            == mocked_time_series.geography.geography_type.name
        )
        assert api_time_series.metric == mocked_time_series.metric.name
        assert api_time_series.stratum == mocked_time_series.stratum.name

        assert api_time_series.sex == mocked_time_series.sex

        assert api_time_series.year == mocked_time_series.year
        assert api_time_series.epiweek == mocked_time_series.epiweek

        assert api_time_series.dt == mocked_time_series.dt
        assert api_time_series.metric_value == mocked_time_series.metric_value
