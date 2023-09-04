from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from metrics.data.managers.api_models.time_series import APITimeSeriesManager
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreTimeSeries
from metrics.data.operations.api_models_beta import (
    create_api_time_series_from_core_time_series,
    generate_api_time_series,
)

MODULE_PATH: str = "metrics.data.operations.api_models_beta"


@pytest.fixture
def mocked_empty_api_time_series_manager() -> mock.Mock:
    mocked_manager = mock.Mock(spec_set=APITimeSeriesManager)
    # If there are existing API time series records
    # Then `generate_api_time_series()` returns early
    mocked_manager.exists.return_value = False
    return mocked_manager


class TestGenerateAPITimeSeries:
    @mock.patch(f"{MODULE_PATH}.create_api_time_series_from_core_time_series")
    def test_calls_bulk_create_on_api_time_series_manager(
        self,
        mocked_create_api_time_series_from_core_time_series: mock.MagicMock,
        mocked_empty_api_time_series_manager: mock.Mock,
    ):
        """
        Given a `APITimeSeriesManager` and a list of mocked `CoreTimeSeries` instances
        When `generate_api_time_series()` is called
        Then `bulk_create()` is called from the `APITimeSeriesManager` with the correct args.

        Patches:
          `mocked_create_api_time_series_from_core_time_series`: Isolation of the
                return values to be passed to the main assertion.
        """
        # Given
        spy_api_time_series_manager = mocked_empty_api_time_series_manager
        mocked_core_time_series = [
            mock.Mock(spec=CoreTimeSeries),
            mock.Mock(spec=CoreTimeSeries),
        ]

        # When
        generate_api_time_series(
            all_core_time_series=mocked_core_time_series,
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
    def test_calls_create_api_time_series_from_core_time_series_on_core_time_series(
        self,
        spy_create_api_time_series_from_core_time_series: mock.MagicMock,
        mocked_empty_api_time_series_manager,
    ):
        """
        Given an `APITimeSeriesManager` and a list of mocked `CoreTimeSeries` instances
        When `generate_weekly_time_series()` is called
        Then `create_api_time_series_from_core_time_series()` with the correct args
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)

        # When
        generate_api_time_series(
            all_core_time_series=[mocked_time_series],
            api_time_series_manager=mocked_empty_api_time_series_manager,  # stubbed
        )

        # Then
        assert spy_create_api_time_series_from_core_time_series.mock_calls == [
            mock.call(
                core_time_series=mocked_time_series,
                theme=mocked_time_series.metric.topic.sub_theme.theme.name,
                sub_theme=mocked_time_series.metric.topic.sub_theme.name,
                topic=mocked_time_series.metric.topic.name,
                metric=mocked_time_series.metric.name,
                metric_group=mocked_time_series.metric.metric_group.name,
                metric_frequency=mocked_time_series.metric_frequency,
                refresh_date=mocked_time_series.refresh_date,
            )
        ]

    def test_bulk_create_not_called_on_api_time_series_manager_when_returning_early(
        self, caplog: LogCaptureFixture
    ):
        """
        Given an `APITimeSeriesManager` and no provided `CoreTimeSeries` instances
        When `generate_weekly_time_series()` is called
        Then the correct log is made
        And `bulk_create()` is not called from the `APITimeSeriesManager`
        """
        # Given
        spy_api_time_series_manager = mock.Mock()
        spy_api_time_series_manager.exists.return_value = True

        # When
        generate_api_time_series(
            all_core_time_series=[],
            api_time_series_manager=spy_api_time_series_manager,
        )

        # Then
        log_text = "No CoreTimeSeries provided, therefore no APITimeSeries records will be created"
        assert log_text in caplog.text
        spy_api_time_series_manager.bulk_create.assert_called_once_with(
            objs=[], batch_size=100
        )


class TestCreateAPITimeSeriesFromCoreTimeSeries:
    def test_uses_correct_fields_from_core_time_series(self):
        """
        Given a mocked `CoreTimeSeries` object
        When `create_api_time_series_from_core_time_series()` is called
        Then an `APITimeSeries` object is created
        And it takes the new fields from the `CoreTimeSeries` object
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)

        # When
        api_time_series = create_api_time_series_from_core_time_series(
            core_time_series=mocked_time_series
        )

        # Then
        assert isinstance(api_time_series, APITimeSeries)
        assert (
            api_time_series.geography_code
            == mocked_time_series.geography.geography_code
        )
        assert api_time_series.age == mocked_time_series.age.name
        assert api_time_series.month == mocked_time_series.month
        assert (
            api_time_series.metric_group == mocked_time_series.metric.metric_group.name
        )
        assert api_time_series.refresh_date == mocked_time_series.refresh_date

    def test_uses_explicit_fields_from_call(self):
        """
        Given a mocked `CoreTimeSeries` object
        And a number of pre-defined fields
        When `create_api_time_series_from_core_time_series()` is called
        Then an `APITimeSeries` object is created with the correct fields
        """
        # Given
        mocked_time_series = mock.Mock(spec=CoreTimeSeries)
        fake_theme = "infectious_disease"
        fake_sub_theme = "respiratory"
        fake_topic = "COVID-19"
        fake_metric = "COVID-19_cases_casesByDay"
        fake_metric_group = "cases"
        fake_metric_frequency = "W"
        fake_refresh_date = "2023-08-03"

        # When
        api_time_series = create_api_time_series_from_core_time_series(
            core_time_series=mocked_time_series,
            theme=fake_theme,
            sub_theme=fake_sub_theme,
            topic=fake_topic,
            metric=fake_metric,
            metric_group=fake_metric_group,
            metric_frequency=fake_metric_frequency,
            refresh_date=fake_refresh_date,
        )

        # Then
        assert isinstance(api_time_series, APITimeSeries)
        assert api_time_series.theme == fake_theme
        assert api_time_series.sub_theme == fake_sub_theme
        assert api_time_series.topic == fake_topic
        assert api_time_series.metric == fake_metric
        assert api_time_series.metric_group == fake_metric_group
        assert api_time_series.metric_frequency == fake_metric_frequency
        assert api_time_series.refresh_date == fake_refresh_date
