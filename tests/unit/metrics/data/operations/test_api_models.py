from unittest import mock

from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries
from metrics.data.operations.api_models import (
    create_api_time_series_from_core_time_series,
    generate_api_time_series,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager

MODULE_PATH: str = "metrics.data.operations.api_models"


class TestGenerateWeeklyTimeSeries:
    @mock.patch(f"{MODULE_PATH}.create_api_time_series_from_core_time_series")
    def test_calls_bulk_create_on_all_api_time_series(
        self, mocked_create_api_time_series_from_core_time_series: mock.MagicMock
    ):
        """
        Given a `APITimeManager` and a `FakeTimeSeriesManager`.
        When `generate_api_time_series()` is called.
        Then `bulk_create()` is called from the `APITimeManager` with the correct args.

        Patches:
          `create_weekly_time_series_from_core_time_series`: Isolation of the
                return values to be passed to the main assertion.
        """
        # Given
        spy_api_time_series_manager = mock.Mock()

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
        self, mocked_create_api_time_series_from_core_time_series: mock.MagicMock
    ):
        """
        Given a `TimeSeriesManager` and a mocked `TimeSeries` object
        When `generate_weekly_time_series()` is called.
        Then `create_weekly_time_series_from_core_time_series()` with the correct args.
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)
        mocked_time_series_manager = mock.Mock()
        mocked_time_series_manager.all_related.return_value = [mocked_time_series]

        # When
        generate_api_time_series(
            core_time_series_manager=mocked_time_series_manager,
            api_time_series_manager=mock.Mock(),  # stubbed
        )

        # Then
        assert mocked_create_api_time_series_from_core_time_series.mock_calls == [
            mock.call(core_time_series=mocked_time_series)
        ]


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
