from unittest import mock

from metrics.api import enums
from metrics.api.models.api_models import WeeklyTimeSeries
from metrics.api.models.core_models import TimeSeries
from metrics.data.operations.api_models import (
    create_weekly_time_series_from_core_time_series,
    generate_weekly_time_series,
)
from tests.fakes.managers.time_series_manager import FakeTimeSeriesManager

MODULE_PATH: str = "data.operations.api_models"


class TestGenerateWeeklyTimeSeries:
    @mock.patch(f"{MODULE_PATH}.create_weekly_time_series_from_core_time_series")
    def test_calls_bulk_create_on_all_weekly_time_series(
        self, mocked_create_weekly_time_series_from_core_time_series: mock.MagicMock
    ):
        """
        Given a `WeeklyTimeManager` and a `FakeTimeSeriesManager`.
        When `generate_weekly_time_series()` is called.
        Then `bulk_create()` is called from the `WeeklyTimeManager` with the correct args.

        Patches:
          `create_weekly_time_series_from_core_time_series`: Isolation of the
                return values to be passed to the main assertion.
        """
        # Given
        spy_weekly_time_series_manager = mock.Mock()
        weekly_time_period_enum_value: str = enums.TimePeriod.Weekly.value
        mocked_time_series = [
            mock.Mock(spec=TimeSeries, period=weekly_time_period_enum_value),
            mock.Mock(spec=TimeSeries, period=weekly_time_period_enum_value),
            mock.Mock(spec=TimeSeries, period=enums.TimePeriod.Daily.value),
        ]

        # When
        generate_weekly_time_series(
            time_series_manager=FakeTimeSeriesManager(time_series=mocked_time_series),
            weekly_time_series_manager=spy_weekly_time_series_manager,
        )

        # Then
        expected_created_weekly_time_series = [
            mocked_create_weekly_time_series_from_core_time_series.return_value
        ] * 2
        spy_weekly_time_series_manager.bulk_create.assert_called_once_with(
            objs=expected_created_weekly_time_series
        )

    @mock.patch(f"{MODULE_PATH}.create_weekly_time_series_from_core_time_series")
    def test_calls_create_weekly_time_series_from_core_time_series_on_filtered_time_series(
        self, mocked_create_weekly_time_series_from_core_time_series: mock.MagicMock
    ):
        """
        Given a `TimeSeriesManager` and a mocked `TimeSeries` object
        When `generate_weekly_time_series()` is called.
        Then `create_weekly_time_series_from_core_time_series()` with the correct args.
        """
        # Given
        mocked_time_series = mock.Mock(
            spec=TimeSeries, period=enums.TimePeriod.Weekly.value
        )
        mocked_time_series_manager = mock.Mock()
        mocked_time_series_manager.filter_weekly.return_value = [mocked_time_series]

        # When
        generate_weekly_time_series(
            time_series_manager=mocked_time_series_manager,
            weekly_time_series_manager=mock.Mock(),  # stubbed
        )

        # Then
        assert mocked_create_weekly_time_series_from_core_time_series.mock_calls == [
            mock.call(core_time_series=mocked_time_series)
        ]


class TestCreateWeeklyTimeSeriesFromCoreTimeSeries:
    def test_uses_correct_fields_from_core_time_series(self):
        """
        Given a mocked `TimeSeries` object
        When `weekly_time_series()` is called
        Then a `WeeklyTimeSeries` object is created
        And it takes the correct fields from the `TimeSeries` object
        """
        # Given
        mocked_time_series = mock.Mock(spec=TimeSeries)

        # When
        weekly_time_series = create_weekly_time_series_from_core_time_series(
            core_time_series=mocked_time_series
        )

        # Then
        assert isinstance(weekly_time_series, WeeklyTimeSeries)

        assert (
            weekly_time_series.theme
            == mocked_time_series.metric.topic.sub_theme.theme.name
        )
        assert (
            weekly_time_series.sub_theme
            == mocked_time_series.metric.topic.sub_theme.name
        )
        assert weekly_time_series.topic == mocked_time_series.metric.topic.name
        assert weekly_time_series.geography == mocked_time_series.geography.name
        assert (
            weekly_time_series.geography_type
            == mocked_time_series.geography.geography_type.name
        )
        assert weekly_time_series.metric == mocked_time_series.metric.name
        assert weekly_time_series.stratum == mocked_time_series.stratum.name

        assert weekly_time_series.year == mocked_time_series.year
        assert weekly_time_series.epiweek == mocked_time_series.epiweek
        assert weekly_time_series.start_date == mocked_time_series.start_date
        assert weekly_time_series.metric_value == mocked_time_series.metric_value
