import datetime
import decimal

import pytest
from django.utils import timezone

from metrics.data.managers.core_models.time_series import CoreTimeSeriesQuerySet
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models import get_date_n_months_ago_from_timestamp
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory
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
    def test_query_for_data_returns_full_records_when_axes_not_provided(
        self,
    ):
        """
        Given existing `CoreTimeSeries` records
        And no value for the "y_axis"
        When `query_for_data()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then only the returned queryset contains the full records
        """
        # Given
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
        retrieved_records = CoreTimeSeries.objects.query_for_data(
            fields_to_export=[],
            topic=core_time_series[0].metric.topic.name,
            metric=core_time_series[0].metric.name,
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

    @pytest.mark.django_db
    def test_query_for_data_excludes_non_public_records_when_restrict_to_public_is_true(
        self,
    ):
        """
        Given public and non-public `CoreTimeSeries` records
        When `query_for_data()` is called
            from an instance of the `CoreTimeSeriesQueryset`
            with `restrict_to_public` given as True
        Then only the public record is returned
        """
        # Given
        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1, date="2023-01-01", is_public=True
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            metric_value=2, date="2023-01-02", is_public=False
        )

        # When
        retrieved_records = CoreTimeSeries.objects.get_queryset().query_for_data(
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            date_from="2020-01-01",
            date_to="2025-12-31",
            restrict_to_public=True,
        )

        # Then
        assert public_record in retrieved_records
        assert non_public_record not in retrieved_records

    @pytest.mark.django_db
    def test_query_for_data_includes_non_public_records_when_restrict_to_public_is_false(
        self,
    ):
        """
        Given public and non-public `CoreTimeSeries` records
        When `query_for_data()` is called
            from an instance of the `CoreTimeSeriesQueryset`
            with `restrict_to_public` given as False
        Then the non-public record is also returned
        """
        # Given
        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1, date="2023-01-01", is_public=True
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            metric_value=2, date="2023-01-02", is_public=False
        )

        # When
        retrieved_records = CoreTimeSeries.objects.get_queryset().query_for_data(
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            date_from="2020-01-01",
            date_to="2025-12-31",
            restrict_to_public=False,
        )

        # Then
        assert public_record in retrieved_records
        assert non_public_record in retrieved_records


class TestCoreTimeSeriesManager:
    @pytest.mark.django_db
    def test_query_for_data_returns_latest_records_for_multiple_versions(
        self,
    ):
        """
        Given a number of `CoreTimeSeries` records which are stale
        And a number of `CoreTimeSeries` records which are live,
            but not grouped linearly.
        When `query_for_data()` is called
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
        retrieved_records = CoreTimeSeries.objects.query_for_data(
            fields_to_export=["date", "metric_value"],
            topic=expected_fourth_round_for_first_date.metric.topic.name,
            metric=expected_fourth_round_for_first_date.metric.name,
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
    ) -> dict[str, datetime.date | decimal.Decimal]:
        year, month, day = record.date.split("-")

        return {
            "date": datetime.date(
                year=int(year),
                month=int(month),
                day=int(day),
            ),
            "metric_value": decimal.Decimal(record.metric_value),
        }

    @pytest.mark.django_db
    def test_query_for_data_excludes_embargoed_data(self):
        """
        Given a number of `CoreTimeSeries` records which are live
        And a number of `CoreTimeSeries` records which are under embargo
        When `query_for_data()` is called
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
        retrieved_records = CoreTimeSeries.objects.query_for_data(
            fields_to_export=["date", "metric_value"],
            topic=live_core_time_series_records[0].metric.topic.name,
            metric=live_core_time_series_records[0].metric.name,
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

    @pytest.mark.django_db
    def test_delete_superseded_data_deletes_stale_records_only(
        self,
        timestamp_2_months_from_now: datetime.datetime,
    ):
        """
        Given a number of `CoreTimeSeries` records which are stale
        And a number of `CoreTimeSeries` records which are live,
            but not grouped linearly.
        And an embargoed record
        When `delete_superseded_data()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then only the stale `CoreTimeSeries` records are deleted
        And the live & embargoed records are still available
        """
        # Given
        dates = FAKE_DATES
        first_round_outdated_refresh_date = "2023-08-10"
        second_round_refresh_date = "2023-08-11"
        third_round_refresh_date = "2023-08-12"
        fourth_round_refresh_date = "2023-08-13"

        # Our first round of records which are all considered outdated
        stale_first_round_records = [
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
        expected_live_second_round_for_second_date: CoreTimeSeries = (
            partially_stale_second_round_versions[1]
        )
        # In this 3rd round we received updates for only the last of the `dates`
        last_date: str = dates[-1]
        expected_live_third_version_for_third_date: CoreTimeSeries = (
            CoreTimeSeriesFactory.create_record(
                metric_value=3, date=last_date, refresh_date=third_round_refresh_date
            )
        )
        # In the 4th round, we received an update for only the first of the `dates`
        first_date: str = dates[0]
        expected_live_fourth_round_for_first_date: CoreTimeSeries = (
            CoreTimeSeriesFactory.create_record(
                metric_value=4, date=first_date, refresh_date=fourth_round_refresh_date
            )
        )
        # In the 5th and final round, we received an update for only the first date
        # but because this is not yet released from embargo, we do not consider it.
        embargoed_fifth_round_for_first_date: CoreTimeSeries = (
            CoreTimeSeriesFactory.create_record(
                metric_value=5,
                date=first_date,
                refresh_date=fourth_round_refresh_date,
                embargo=timestamp_2_months_from_now,
            )
        )

        # When
        CoreTimeSeries.objects.delete_superseded_data(
            metric=expected_live_fourth_round_for_first_date.metric.name,
            geography=expected_live_fourth_round_for_first_date.geography.name,
            geography_code=expected_live_fourth_round_for_first_date.geography.geography_code,
            geography_type=expected_live_fourth_round_for_first_date.geography.geography_type.name,
            stratum=expected_live_fourth_round_for_first_date.stratum.name,
            age=expected_live_fourth_round_for_first_date.age.name,
            sex=expected_live_fourth_round_for_first_date.sex,
            is_public=expected_live_fourth_round_for_first_date.is_public,
        )
        retrieved_records = CoreTimeSeries.objects.all()

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

        for stale_first_round_record in stale_first_round_records:
            assert stale_first_round_record not in retrieved_records

        assert partially_stale_second_round_versions[0] not in retrieved_records
        assert partially_stale_second_round_versions[2] not in retrieved_records

        assert expected_live_second_round_for_second_date in retrieved_records
        assert expected_live_third_version_for_third_date in retrieved_records
        assert expected_live_fourth_round_for_first_date in retrieved_records
        assert embargoed_fifth_round_for_first_date in retrieved_records

    @pytest.mark.django_db
    def test_find_latest_released_embargo_for_metrics(self):
        """
        Given a number of `CoreTimeSeries` records
            for different metrics
        When `find_latest_released_embargo_for_metrics()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then the latest released embargo timestamp is returned
        """
        # Given
        covid_metric = "COVID-19_deaths_ONSByWeek"
        covid_metric_for_outdated_embargo = "COVID-19_cases_rateRollingMean"

        superseded_embargo = datetime.datetime(
            year=2024, month=1, day=1, hour=1, minute=1, second=1, tzinfo=datetime.UTC
        )
        latest_released_embargo = datetime.datetime(
            year=2024, month=2, day=2, hour=1, minute=2, second=2, tzinfo=datetime.UTC
        )
        last_unreleased_embargo = get_date_n_months_ago_from_timestamp(
            datetime_stamp=timezone.now(), number_of_months=-1
        )

        CoreTimeSeriesFactory.create_record(
            metric_name=covid_metric, embargo=latest_released_embargo
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=covid_metric_for_outdated_embargo, embargo=superseded_embargo
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="hMPV_testing_positivityByWeek", embargo=last_unreleased_embargo
        )

        # When
        extracted_embargo = (
            CoreTimeSeries.objects.find_latest_released_embargo_for_metrics(
                metrics=[covid_metric, covid_metric_for_outdated_embargo]
            )
        )

        # Then
        assert (
            extracted_embargo
            == latest_released_embargo
            != superseded_embargo
            != last_unreleased_embargo
        )

    @pytest.mark.django_db
    def test_find_latest_released_embargo_for_metrics_returns_none_when_no_data_found(
        self,
    ):
        """
        Given no existing `CoreTimeSeries` records
        When `find_latest_released_embargo_for_metrics()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then None is returned
        """
        # Given
        covid_metric = "COVID-19_deaths_ONSByWeek"

        # When
        extracted_embargo = (
            CoreTimeSeries.objects.find_latest_released_embargo_for_metrics(
                metrics=[covid_metric]
            )
        )

        # Then
        assert extracted_embargo is None

    @pytest.mark.django_db
    def test_query_for_data_returns_non_public_record_with_acceptable_permissions(self):
        """
        Given public and non-public `CoreTimeSeries` records
        And an `RBACPermission` which gives access to the non-public portion of the data
        When `query_for_data()` is called from the `CoreTimeSeriesManager`
        Then the non-public record is included
        """
        # Given
        public_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-01", metric_value=1, is_public=True
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-02", metric_value=2, is_public=False
        )

        params_for_query = {
            "theme_name": public_record.metric.topic.sub_theme.theme.name,
            "sub_theme_name": public_record.metric.topic.sub_theme.name,
            "topic_name": public_record.metric.topic.name,
            "metric_name": public_record.metric.name,
            "geography_name": public_record.geography.name,
            "geography_type_name": public_record.geography.geography_type.name,
        }
        params = {k.split("_name")[0]: v for k, v in params_for_query.items()}
        rbac_permission = RBACPermissionFactory.create_record(**params)

        # When
        core_time_series_queryset = CoreTimeSeries.objects.query_for_data(
            **params_for_query,
            date_from="2020-01-01",
            date_to="2025-12-31",
            fields_to_export=[],
            rbac_permissions=[rbac_permission],
        )

        # Then
        assert public_record in core_time_series_queryset
        assert non_public_record in core_time_series_queryset

    @pytest.mark.django_db
    def test_query_for_data_excludes_non_public_record_without_permissions(self):
        """
        Given public and non-public `CoreTimeSeries` records
        And no `RBACPermission` which allows access to the non-public portion of this dataset
        When `query_for_data()` is called from the `CoreTimeSeriesManager`
        Then the non-public record is excluded
        """
        # Given
        public_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-01", metric_value=1, is_public=True
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-02", metric_value=2, is_public=False
        )
        rbac_permission = RBACPermissionFactory.create_record(
            theme="some_other_theme",
            sub_theme=None,
            topic=None,
            metric=None,
            geography=None,
            geography_type=None,
        )

        # When
        core_time_series_queryset = CoreTimeSeries.objects.query_for_data(
            theme=public_record.metric.topic.sub_theme.theme.name,
            sub_theme=public_record.metric.topic.sub_theme.name,
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            geography=public_record.geography.name,
            geography_type=public_record.geography.geography_type.name,
            fields_to_export=[],
            rbac_permissions=[rbac_permission],
            date_from="2020-01-01",
            date_to="2025-12-31",
        )

        # Then
        assert public_record in core_time_series_queryset
        assert non_public_record not in core_time_series_queryset
