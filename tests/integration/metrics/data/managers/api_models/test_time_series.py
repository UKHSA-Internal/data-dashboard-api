import datetime

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from metrics.data.managers.api_models.time_series import APITimeSeriesQuerySet
from metrics.data.models.api_models import APITimeSeries
from metrics.domain.models import get_date_n_months_ago_from_timestamp
from tests.factories.metrics.api_models.time_series import APITimeSeriesFactory

FAKE_DATES = ("2023-01-01", "2023-01-02", "2023-01-03")


class TestAPITimeSeriesQuerySet:
    @pytest.mark.django_db
    def test_filter_for_latest_refresh_date_records_returns_latest_records_for_multiple_versions(
        self,
    ):
        """
        Given a number of `APITimeSeries` records which are stale
        And a number of `APITimeSeries` records which are live,
            but not grouped linearly.
        When `filter_for_latest_refresh_date_records()` is called
            from an instance of `APITimeSeriesQueryset`
        Then only the live group of `APITimeSeries` records are returned
        """
        # Given
        dates = FAKE_DATES
        first_round_outdated_refresh_date = "2023-08-10"
        second_round_refresh_date = "2023-08-11"
        third_round_refresh_date = "2023-08-12"
        fourth_round_refresh_date = "2023-08-13"

        # Our first round of records which are all considered outdated
        stale_first_round_versions = [
            APITimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
                refresh_date=first_round_outdated_refresh_date,
            )
            for date in dates
        ]
        # In this 2nd round we received updates for each of the `dates`
        partially_stale_second_round_versions = [
            APITimeSeriesFactory.create_record(
                metric_value=2, date=date, refresh_date=second_round_refresh_date
            )
            for date in dates
        ]
        # In this 3rd round we received updates for only the last of the `dates`
        last_date = dates[-1]
        third_version_for_third_date = APITimeSeriesFactory.create_record(
            metric_value=3, date=last_date, refresh_date=third_round_refresh_date
        )
        # In the 4th and final round, we received an update for only the first of the `dates`
        first_date = dates[0]
        fourth_round_for_first_date = APITimeSeriesFactory.create_record(
            metric_value=4, date=first_date, refresh_date=fourth_round_refresh_date
        )

        # When
        input_queryset = APITimeSeries.objects.all()
        retrieved_records = (
            APITimeSeriesQuerySet().filter_for_latest_refresh_date_records(
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
        Given a number of `APITimeSeries` records which are live
        And a number of `APITimeSeries` records which are under embargo
        When `_exclude_data_under_embargo()` is called
            from an instance of `APITimeSeriesQueryset`
        Then only the live group of `APITimeSeries` records are returned
        """
        # Given
        current_time = timezone.now()
        dates = FAKE_DATES
        live_api_time_series_records = [
            APITimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
            )
            for date in dates
        ]

        embargo_point_in_time = current_time + datetime.timedelta(days=7)
        embargoed_api_time_series_records = [
            APITimeSeriesFactory.create_record(
                metric_value=2,
                date=date,
                embargo=embargo_point_in_time,
            )
            for date in dates
        ]

        # When
        input_queryset = APITimeSeries.objects.get_queryset()
        filtered_queryset = input_queryset._exclude_data_under_embargo(
            queryset=input_queryset
        )

        # Then
        # All the live records should be in the returned queryset
        assert all(
            live_record
            for live_record in live_api_time_series_records
            if live_record in filtered_queryset
        )
        # None of the embargo records should be in the returned queryset
        assert not any(
            embargoed_record
            for embargoed_record in embargoed_api_time_series_records
            if embargoed_record in filtered_queryset
        )

    @pytest.mark.django_db
    def test_data_with_no_embargo_set_is_returned(self):
        """
        Given a number of `APITimeSeries` records which are live
        And a number of `APITimeSeries` records which have been
            designated to be immediately queryable with a `None` embargo value
        When `_exclude_data_under_embargo()` is called
            from an instance of `APITimeSeriesQueryset`
        Then only the newer immediately unembargoed
            group of `APITimeSeries` records are returned
        """
        # Given
        original_metric_value = 1
        dates = FAKE_DATES
        embargo = datetime.datetime(
            year=2023, month=12, day=1, hour=12, minute=0, second=0
        )
        original_refresh_date = datetime.datetime(year=2023, month=11, day=1)
        live_api_time_series_records = [
            APITimeSeriesFactory.create_record(
                metric_value=original_metric_value,
                date=date,
                embargo=embargo,
                refresh_date=original_refresh_date,
            )
            for date in dates
        ]

        updated_refresh_date = datetime.datetime(year=2023, month=11, day=8)
        immediately_unembargoed_metric_value = 2
        embargoed_api_time_series_records = [
            APITimeSeriesFactory.create_record(
                metric_value=immediately_unembargoed_metric_value,
                date=date,
                embargo=None,
                refresh_date=updated_refresh_date,
            )
            for date in dates
        ]

        # When
        input_queryset = APITimeSeries.objects.get_queryset()
        api_time_series = live_api_time_series_records[0]
        retrieved_records = input_queryset.filter_for_list_view(
            theme_name=api_time_series.theme,
            sub_theme_name=api_time_series.sub_theme,
            topic_name=api_time_series.topic,
            geography_type_name=api_time_series.geography_type,
            geography_name=api_time_series.geography,
            metric_name=api_time_series.metric,
        )

        # Then
        # All the 'live' records should not be in the returned queryset
        assert not any(
            live_record
            for live_record in live_api_time_series_records
            if live_record in retrieved_records
        )
        # And the immediately unembargoed records should be in the returned queryset
        assert all(
            embargoed_record
            for embargoed_record in embargoed_api_time_series_records
            if embargoed_record in retrieved_records
        )

    @pytest.mark.django_db
    def test_filter_for_list_view_excludes_embargoed_data(self):
        """
        Given a number of `APITimeSeries` records which are live
        And a number of `APITimeSeries` records which are under embargo
        When `filter_for_list_view()` is called
            from an instance of `APITimeSeriesQueryset`
        Then only the live group of `APITimeSeries` records are returned
        """
        # Given
        dates = FAKE_DATES
        current_time = timezone.now()

        # 1st round of records which are considered to be live
        live_api_time_series_records = [
            APITimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
            )
            for date in dates
        ]

        # 2nd round of records which are considered to be under embargo
        # and therefore should not be made available by the query
        embargo_point_in_time = current_time + datetime.timedelta(days=7)
        embargoed_api_time_series_records = [
            APITimeSeriesFactory.create_record(
                metric_value=2,
                date=date,
                embargo=embargo_point_in_time,
            )
            for date in dates
        ]

        # When
        api_time_series = live_api_time_series_records[0]
        input_queryset = APITimeSeries.objects.get_queryset()
        retrieved_records = input_queryset.filter_for_list_view(
            theme_name=api_time_series.theme,
            sub_theme_name=api_time_series.sub_theme,
            topic_name=api_time_series.topic,
            geography_type_name=api_time_series.geography_type,
            geography_name=api_time_series.geography,
            metric_name=api_time_series.metric,
        )

        # Then
        # Our database will look like the following:
        # | 2023-01-01 | 2023-01-02 | 2023-01-03 |
        # | 1st round  | 1st round  | 1st round  |   <- live
        # | 2nd round  | 2nd round  | 2nd round  |   <- under embargo
        # ----------------------------------------
        # | 1st round  | 1st round  | 1st round  |   <- expected results

        assert retrieved_records.count() == 3

        # Then
        # All the live records should be in the returned queryset
        assert all(
            live_record
            for live_record in live_api_time_series_records
            if live_record in retrieved_records
        )
        # None of the embargo records should be in the returned queryset
        assert not any(
            embargoed_record
            for embargoed_record in embargoed_api_time_series_records
            if embargoed_record in retrieved_records
        )

    @pytest.mark.django_db
    def test_records_with_different_latest_refresh_dates(self):
        """
        Given a number of `APITimeSeries` records
            whereby each age-group has a different
            latest refresh date associated with the age group
        When `filter_for_list_view()` is called
            from an instance of `APITimeSeriesQueryset`
        Then the latest refreshed value for each age group
            is returned independent of the latest refresh date
            when compare to other age groupings
        """
        # Given
        metric = "influenza_healthcare_ICUHDUadmissionRateByWeek"
        first_date = "2024-01-01"
        second_date = "2024-01-02"
        expected_current_records: list[APITimeSeries] = (
            self._create_api_timeseries_with_mixed_age_date_refresh_dates(
                metric=metric,
                first_date=first_date,
                second_date=second_date,
            )
        )

        # When
        retrieved_records = APITimeSeries.objects.get_queryset().filter_for_list_view(
            theme_name=expected_current_records[0].theme,
            sub_theme_name=expected_current_records[0].sub_theme,
            topic_name=expected_current_records[0].topic,
            geography_type_name=expected_current_records[0].geography_type,
            geography_name=expected_current_records[0].geography,
            metric_name=metric,
        )

        # Then
        # Our database will look like the following:
        #                            |                      refresh_date                 |                  |
        # |------------------------------------------------------------------------------|------------------|
        # |     date    |    age     | 2024-02-01 | 2024-01-24 | 2024-01-18 | 2024-01-11 | expected results |
        # |------------------------------------------------------------------------------|------------------|
        # |  2024-01-01 |   00-04    | 4th round  | 3rd round  | 2nd round  | 1st round  |    4th round     |
        # |(first date) |   05-14    |    N/A     |    N/A     | 2nd round  | 1st round  |    2nd round     |
        # |             |   55-64    | 2nd round  |    N/A     | 1st round  |    N/A     |    2nd round     |
        # |------------------------------------------------------------------------------|------------------|
        # |  2024-01-02 |   00-04    | 3rd round  | 2nd round  |    N/A     | 1st round  |    3rd round     |
        # |(second date)|   05-14    |    N/A     | 2nd round  |    N/A     | 1st round  |    2nd round     |
        # |             |   55-64    |    N/A     |    N/A     |    N/A     |  N/A       |       N/A        |
        # |------------------------------------------------------------------------------|------------------|
        # We expect the latest record associated with each age/sex/stratum group on a date-by-date basis to be returned

        assert retrieved_records.count() == len(expected_current_records)
        assert all(
            expected_current_record in retrieved_records
            for expected_current_record in expected_current_records
        )

    @staticmethod
    def _create_api_timeseries_with_mixed_age_date_refresh_dates(
        metric: str, first_date: str, second_date: str
    ) -> list[APITimeSeries]:
        current_0_to_4_record_first_date = APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.3,
            refresh_date="2024-02-01",
            date=first_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.31,
            refresh_date="2024-01-24",
            date=first_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.35,
            refresh_date="2024-01-18",
            date=first_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.37,
            refresh_date="2024-01-11",
            date=first_date,
        )
        current_5_to_14_record_first_date = APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="05-14",
            metric_value=0.07,
            refresh_date="2024-01-18",
            date=first_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="05-14",
            metric_value=0.08,
            refresh_date="2024-01-11",
            date=first_date,
        )
        current_55_to_64_record_first_date = APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="55-64",
            metric_value=0.16,
            refresh_date="2024-02-01",
            date=first_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="55-64",
            metric_value=0.17,
            refresh_date="2024-01-18",
            date=first_date,
        )

        current_0_to_4_record_second_date = APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.24,
            refresh_date="2024-02-01",
            date=second_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.13,
            refresh_date="2024-01-24",
            date=second_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="00-04",
            metric_value=0.11,
            refresh_date="2024-01-11",
            date=second_date,
        )
        current_5_to_14_record_second_date = APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="05-14",
            metric_value=0.09,
            refresh_date="2024-01-24",
            date=second_date,
        )
        APITimeSeriesFactory.create_record(
            metric_name=metric,
            age_name="05-14",
            metric_value=0.02,
            refresh_date="2024-01-11",
            date=second_date,
        )

        return [
            # 1st date records
            current_0_to_4_record_first_date,
            current_5_to_14_record_first_date,
            current_55_to_64_record_first_date,
            # 2nd date records
            current_0_to_4_record_second_date,
            current_5_to_14_record_second_date,
        ]


class TestAPITimeSeriesManager:
    @pytest.mark.django_db
    def test_delete_superseded_data_deletes_stale_records_only(
        self, timestamp_2_months_from_now: datetime.datetime
    ):
        """
        Given a number of `APITimeSeries` records which are stale
        And a number of `APITimeSeries` records which are live,
            but not grouped linearly.
        And a record which is under embargo
        When `delete_superseded_data()` is called
            from an instance of `APITimeSeriesQueryset`
        Then only the stale `APITimeSeries` records are deleted
        And the live & embargoed records are still available
        """
        # Given
        dates = FAKE_DATES
        first_round_outdated_refresh_date = "2023-08-10"
        second_round_refresh_date = "2023-08-11"
        third_round_refresh_date = "2023-08-12"
        fourth_round_refresh_date = "2023-08-13"
        fifth_round_refresh_date = "2023-08-14"

        # Our first round of records which are all considered outdated
        stale_first_round_versions = [
            APITimeSeriesFactory.create_record(
                metric_value=1,
                date=date,
                refresh_date=first_round_outdated_refresh_date,
            )
            for date in dates
        ]
        # In this 2nd round we received updates for each of the `dates`
        partially_stale_second_round_versions = [
            APITimeSeriesFactory.create_record(
                metric_value=2, date=date, refresh_date=second_round_refresh_date
            )
            for date in dates
        ]
        # In this 3rd round we received updates for only the last of the `dates`
        last_date = dates[-1]
        live_third_version_for_third_date = APITimeSeriesFactory.create_record(
            metric_value=3, date=last_date, refresh_date=third_round_refresh_date
        )
        # In the 4th round, we received an update for only the first of the `dates`
        first_date = dates[0]
        fourth_round_for_first_date = APITimeSeriesFactory.create_record(
            metric_value=4, date=first_date, refresh_date=fourth_round_refresh_date
        )
        # In the 5th and final round, we received an update for only the first date
        # but because this is not yet released from embargo, we do not consider it.
        fifth_embargoed_round_for_first_date = APITimeSeriesFactory.create_record(
            metric_value=5,
            date=first_date,
            refresh_date=fifth_round_refresh_date,
            embargo=timestamp_2_months_from_now,
        )

        # When
        APITimeSeries.objects.delete_superseded_data(
            theme_name=fifth_embargoed_round_for_first_date.theme,
            sub_theme_name=fifth_embargoed_round_for_first_date.sub_theme,
            topic_name=fifth_embargoed_round_for_first_date.topic,
            metric_name=fifth_embargoed_round_for_first_date.metric,
            geography_name=fifth_embargoed_round_for_first_date.geography,
            geography_type_name=fifth_embargoed_round_for_first_date.geography_type,
            geography_code=fifth_embargoed_round_for_first_date.geography_code,
            stratum_name=fifth_embargoed_round_for_first_date.stratum,
            sex=fifth_embargoed_round_for_first_date.sex,
            age=fifth_embargoed_round_for_first_date.age,
        )
        retrieved_records = APITimeSeries.objects.all()

        # Then
        # Our database will look like the following:
        # | 2023-01-01 | 2023-01-02 | 2023-01-03 |
        # | 1st round  | 1st round  | 1st round  |   <- entirely superseded
        # | 2nd round  | 2nd round  | 2nd round  |   <- partially superseded
        # |     -      |      -     | 3rd round  |   <- contains a final successor but no other updates
        # | 4th round  |      -     |     -      |   <- 'head' round with no successors
        # | 5th round  |      -     |     -      |   <- embargo round not yet released
        # ----------------------------------------
        # | 1st round  | 1st round  | 1st round  |   <- expected records to be deleted
        # | 2nd round  |      -     | 2nd round  |   <- expected records to be deleted

        assert retrieved_records.count() == 4

        # --- Checks for 1st round ---
        # The 1st round was succeeded entirely by the 2nd round
        # So we expect to see none of them in the remaining records
        for stale_first_version_record in stale_first_round_versions:
            assert stale_first_version_record not in retrieved_records

        # --- Checks for 2nd round ---
        stale_first_date_second_version_record = partially_stale_second_round_versions[
            0
        ]
        assert stale_first_date_second_version_record not in retrieved_records

        live_second_date_second_version = partially_stale_second_round_versions[1]
        assert live_second_date_second_version in retrieved_records

        stale_third_date_second_version = partially_stale_second_round_versions[2]
        assert stale_third_date_second_version not in retrieved_records

        # --- Checks for 3rd round ---
        assert live_third_version_for_third_date in retrieved_records

        # --- Checks for 4th round ---
        assert fourth_round_for_first_date in retrieved_records

        # --- Checks for 5th round ---
        assert fifth_embargoed_round_for_first_date in retrieved_records
