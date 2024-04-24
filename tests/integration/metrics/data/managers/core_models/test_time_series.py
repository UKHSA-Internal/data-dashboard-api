import datetime
import decimal

import pytest
from django.utils import timezone

from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreTimeSeries
from tests.factories.metrics.time_series import CoreTimeSeriesFactory

FAKE_DATES = ("2023-01-01", "2023-01-02", "2023-01-03")


class TestCoreTimeSeriesQuerySet:
    @pytest.mark.django_db
    def test_filter_for_latest_refresh_date_records_returns_latest_records_for_multiple_versions(
        self,
    ):
        """
        Given a number of `CoreTimeSeries` records which are stale
        And a number of `CoreTimeSeries` records which are live,
            but not grouped linearly.
        When `filter_for_latest_refresh_date_records()` is called
            from an instance of  `CoreTimeSeriesQueryset`
        Then only the live group of `CoreTimeSeries` records are returned
        """
        # Given
        dates = FAKE_DATES
        first_round_outdated_refresh_date = "2023-08-10"
        second_round_refresh_date = "2023-08-11"
        third_round_refresh_date = "2023-08-12"
        fourth_round_refresh_date = "2023-08-13"

        # Our first round of records which are all considered outdated
        stale_first_round_versions = [
            CoreTimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
                refresh_date=first_round_outdated_refresh_date,
            )
            for date in dates
        ]
        # In this 2nd round we received updates for each of the `dates`
        partially_stale_second_round_versions = [
            CoreTimeSeriesFactory.create_record(
                metric_value=2, date=date, refresh_date=second_round_refresh_date
            )
            for date in dates
        ]
        # In this 3rd round we received updates for only the last of the `dates`
        last_date = dates[-1]
        third_version_for_third_date = CoreTimeSeriesFactory.create_record(
            metric_value=3, date=last_date, refresh_date=third_round_refresh_date
        )
        # In the 4th and final round, we received an update for only the first of the `dates`
        first_date = dates[0]
        fourth_round_for_first_date = CoreTimeSeriesFactory.create_record(
            metric_value=4, date=first_date, refresh_date=fourth_round_refresh_date
        )

        # When
        input_queryset = CoreTimeSeries.objects.all()
        retrieved_records = (
            CoreTimeSeriesQuerySet().filter_for_latest_refresh_date_records(
                queryset=input_queryset
            )
        )

        # Then
        # Our database will look like the following:
        # | 2023-01-01 | 2023-01-02 | 2023-01-03 |
        # | 1st round  | 1st round  | 1st round  |   <- entirely superseded
        # | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded
        # |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
        # | 4th round  |      -     |     -      |   <- 'head' round with no successors
        # ----------------------------------------
        # | 4th round  | 2nd round  | 3rd round  |   <- expected results

        # As such we expect the 1 update from each of the
        # 4th, 2nd and 3rd rounds respectively to be returned from our query
        assert retrieved_records.count() == 3

        # --- Checks for 1st round ---
        # The 1st round was succeeded entirely by the 2nd round
        # So we don't expect to see any of them in the returned records
        for stale_first_version_record in stale_first_round_versions:
            assert stale_first_version_record not in retrieved_records

        # --- Checks for 2nd round ---
        # The 1st date of the 2nd should not be returned because it had was succeeded by the 4th round
        first_date_second_version_record = partially_stale_second_round_versions[0]
        assert first_date_second_version_record not in retrieved_records

        # The 2nd date of the 2nd should be returned because even though it belongs to an 'older' round
        # the subsequent rounds contained no successors
        second_date_second_version = partially_stale_second_round_versions[1]
        assert second_date_second_version in retrieved_records

        # The 3rd date of the 2nd round ended up being succeeded by the `third_version_for_third_date`
        # So we don't expect to see this in the returned records
        third_date_second_version = partially_stale_second_round_versions[2]
        assert third_date_second_version not in retrieved_records

        # --- Checks for 3rd round ---
        # The 3rd round record should be returned since it did not have any successors in the subsequent round
        assert third_version_for_third_date in retrieved_records

        # --- Checks for 4th round ---
        # The 4th round record should be returned since it belongs to the 'head' round and naturally has no successors
        assert fourth_round_for_first_date in retrieved_records

    @pytest.mark.django_db
    def test_exclude_data_under_embargo(self):
        """
        Given a number of `CoreTimeSeries` records which are live
        And a number of `CoreTimeSeries` records which are under embargo
        When `_exclude_data_under_embargo()` is called
            from an instance of  `CoreTimeSeriesQueryset`
        Then only the live group of `CoreTimeSeries` records are returned
        """
        # Given
        current_time = timezone.now()
        dates = FAKE_DATES
        live_core_time_series_records = [
            CoreTimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
            )
            for date in dates
        ]

        embargo_point_in_time = current_time + datetime.timedelta(days=7)
        embargoed_core_time_series_records = [
            CoreTimeSeriesFactory.create_record(
                metric_value=2,
                date=date,
                embargo=embargo_point_in_time,
            )
            for date in dates
        ]

        # When
        input_queryset = CoreTimeSeries.objects.get_queryset()
        filtered_queryset = input_queryset._exclude_data_under_embargo(
            queryset=input_queryset
        )

        # Then
        # All the live records should be in the returned queryset
        assert all(
            live_record
            for live_record in live_core_time_series_records
            if live_record in filtered_queryset
        )
        # None of the embargo records should be in the returned queryset
        assert not any(
            embargoed_record
            for embargoed_record in embargoed_core_time_series_records
            if embargoed_record in filtered_queryset
        )

    @pytest.mark.django_db
    def test_filter_for_x_and_y_values_returns_full_records_when_axes_not_provided(
        self,
    ):
        """
        Given existing `CoreTimeSeries` records
        And no value for the "y_axis"
        When `filter_for_x_and_y_values()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then only the returned queryset contains the full records
        """
        # Given
        x_axis = "date"
        y_axis = ""
        dates = FAKE_DATES
        core_time_series = [
            CoreTimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
                refresh_date=datetime.datetime(year=2023, month=12, day=1),
            )
            for date in dates
        ]
        example_core_time_series = core_time_series[0]

        # When
        retrieved_records = CoreTimeSeries.objects.filter_for_x_and_y_values(
            x_axis=x_axis,
            y_axis=y_axis,
            topic_name=core_time_series[0].metric.topic.name,
            metric_name=core_time_series[0].metric.name,
            date_from=dates[0],
            date_to=dates[-1],
        )

        # Then
        assert retrieved_records[0].metric.name == example_core_time_series.metric.name
        assert (
            retrieved_records[0].metric.topic.name
            == example_core_time_series.metric.topic.name
        )
        assert (
            retrieved_records[0].metric_value == example_core_time_series.metric_value
        )


class TestCoreTimeSeriesManager:
    @pytest.mark.django_db
    def test_filter_for_x_and_y_values_returns_latest_records_for_multiple_versions(
        self,
    ):
        """
        Given a number of `CoreTimeSeries` records which are stale
        And a number of `CoreTimeSeries` records which are live,
            but not grouped linearly.
        When `filter_for_x_and_y_values()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then only the live group of `CoreTimeSeries` records are returned
        """
        # Given
        dates = FAKE_DATES
        first_round_outdated_refresh_date = "2023-08-10"
        second_round_refresh_date = "2023-08-11"
        third_round_refresh_date = "2023-08-12"
        fourth_round_refresh_date = "2023-08-13"

        # Our first round of records which are all considered outdated
        [
            CoreTimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
                refresh_date=first_round_outdated_refresh_date,
            )
            for date in dates
        ]
        # In this 2nd round we received updates for each of the `dates`
        partially_stale_second_round_versions: list[CoreTimeSeries] = [
            CoreTimeSeriesFactory.create_record(
                metric_value=2, date=date, refresh_date=second_round_refresh_date
            )
            for date in dates
        ]
        expected_second_round_for_second_date: CoreTimeSeries = (
            partially_stale_second_round_versions[1]
        )
        # In this 3rd round we received updates for only the last of the `dates`
        last_date: str = dates[-1]
        expected_third_version_for_third_date: CoreTimeSeries = (
            CoreTimeSeriesFactory.create_record(
                metric_value=3, date=last_date, refresh_date=third_round_refresh_date
            )
        )
        # In the 4th and final round, we received an update for only the first of the `dates`
        first_date: str = dates[0]
        expected_fourth_round_for_first_date: CoreTimeSeries = (
            CoreTimeSeriesFactory.create_record(
                metric_value=4, date=first_date, refresh_date=fourth_round_refresh_date
            )
        )

        # When
        retrieved_records = CoreTimeSeries.objects.filter_for_x_and_y_values(
            x_axis="date",
            y_axis="metric_value",
            topic_name=expected_fourth_round_for_first_date.metric.topic.name,
            metric_name=expected_fourth_round_for_first_date.metric.name,
            date_from=dates[0],
            date_to=last_date,
        )

        # Then
        # Our database will look like the following:
        # | 2023-01-01 | 2023-01-02 | 2023-01-03 |
        # | 1st round  | 1st round  | 1st round  |   <- entirely superseded
        # | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded
        # |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
        # | 4th round  |      -     |     -      |   <- 'head' round with no successors
        # ----------------------------------------
        # | 4th round  | 2nd round  | 3rd round  |   <- expected results

        assert retrieved_records.count() == 3

        # As such we expect the 1 update from each of the
        # 4th, 2nd and 3rd rounds respectively to be returned from our query
        assert retrieved_records[0] == self._build_record_representation_in_queryset(
            record=expected_fourth_round_for_first_date
        )
        assert retrieved_records[1] == self._build_record_representation_in_queryset(
            record=expected_second_round_for_second_date
        )
        assert retrieved_records[2] == self._build_record_representation_in_queryset(
            record=expected_third_version_for_third_date
        )

    @staticmethod
    def _build_record_representation_in_queryset(
        record: CoreTimeSeries,
    ) -> tuple[datetime.date, decimal.Decimal]:
        year, month, day = record.date.split("-")

        return (
            datetime.date(
                year=int(year),
                month=int(month),
                day=int(day),
            ),
            decimal.Decimal(record.metric_value),
        )

    @pytest.mark.django_db
    def test_filter_for_x_and_y_values_excludes_embargoed_data(self):
        """
        Given a number of `CoreTimeSeries` records which are live
        And a number of `CoreTimeSeries` records which are under embargo
        When `filter_for_x_and_y_values()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then only the live group of `CoreTimeSeries` records are returned
        """
        # Given
        dates = FAKE_DATES

        # 1st round of records which are considered to be live
        current_time = timezone.now()
        live_core_time_series_records = [
            CoreTimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
            )
            for date in dates
        ]

        # 2nd round of records which are considered to be under embargo
        # and therefore should not be made available by the query
        embargo_point_in_time = current_time + datetime.timedelta(days=7)
        [
            CoreTimeSeriesFactory.create_record(
                metric_value=2,
                date=date,
                embargo=embargo_point_in_time,
            )
            for date in dates
        ]

        # When
        retrieved_records = CoreTimeSeries.objects.filter_for_x_and_y_values(
            x_axis="date",
            y_axis="metric_value",
            topic_name=live_core_time_series_records[0].metric.topic.name,
            metric_name=live_core_time_series_records[0].metric.name,
            date_from=dates[0],
            date_to=dates[-1],
        )

        # Then
        # Our database will look like the following:
        # | 2023-01-01 | 2023-01-02 | 2023-01-03 |
        # | 1st round  | 1st round  | 1st round  |   <- live
        # | 2nd round  | 2nd round  | 2nd round  |   <- under embargo
        # ----------------------------------------
        # | 1st round  | 1st round  | 1st round  |   <- expected results

        assert retrieved_records.count() == 3

        # As such we expect the live records to be returned
        assert retrieved_records[0] == self._build_record_representation_in_queryset(
            record=live_core_time_series_records[0]
        )
        assert retrieved_records[1] == self._build_record_representation_in_queryset(
            record=live_core_time_series_records[1]
        )
        assert retrieved_records[2] == self._build_record_representation_in_queryset(
            record=live_core_time_series_records[2]
        )

    @pytest.mark.django_db
    def test_get_available_geographies(self):
        """
        Given a `topic` and a number of `CoreTimeSeries` records
        When `get_available_geographies()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then the returned results contain the correct geographies
        """
        # Given
        topic = "COVID-19"
        CoreTimeSeriesFactory.create_record(
            geography_type_name="Lower Tier Local Authority",
            geography_name="Hackney",
            topic_name=topic,
        )
        CoreTimeSeriesFactory.create_record(
            geography_type_name="Nation",
            geography_name="England",
            topic_name=topic,
        )

        CoreTimeSeriesFactory.create_record(
            geography_type_name="Lower Tier Local Authority",
            geography_name="Birmingham",
            topic_name="Influenza",
            metric_name="influenza_testing_positivityByWeek",
        )

        # When
        available_geographies = CoreTimeSeries.objects.get_available_geographies(
            topic=topic
        )

        # Then
        assert len(available_geographies) == 2

        # The order is important, we expect the results to be ordered by geography type
        assert available_geographies[0].geography__name == "Hackney"
        assert (
            available_geographies[0].geography__geography_type__name
            == "Lower Tier Local Authority"
        )

        assert available_geographies[1].geography__name == "England"
        assert available_geographies[1].geography__geography_type__name == "Nation"
