import datetime
import decimal
from unittest import mock

import pytest
from django.utils import timezone

from metrics.data.managers.core_models.time_series import (
    CoreTimeSeriesQuerySet,
    _is_geography_permitted,
    filter_geographies_by_permission,
)
from metrics.data.models.core_models import CoreTimeSeries
from tests.factories.metrics.time_series import CoreTimeSeriesFactory

FAKE_DATES = ("2023-01-01", "2023-01-02", "2023-01-03")
MODULE_PATH = "metrics.data.managers.core_models.time_series"


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
    def test_query_for_data_excludes_non_public_records_without_permission_sets(
        self,
    ):
        """
        Given public and non-public `CoreTimeSeries` records
        When `query_for_data()` is called
            from an instance of the `CoreTimeSeriesQueryset`
            with no permission sets provided
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
        )

        # Then
        assert public_record in retrieved_records
        assert non_public_record not in retrieved_records

    @pytest.mark.django_db
    def test_query_for_data_includes_non_public_records_with_global_permission_sets(
        self,
    ):
        """
        Given public and non-public `CoreTimeSeries` records
        When `query_for_data()` is called
            from an instance of the `CoreTimeSeriesQueryset`
            with global permission sets provided
        Then the non-public record is also returned
        """
        # Given
        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1, date="2023-01-01", is_public=True
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            metric_value=2, date="2023-01-02", is_public=False
        )

        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }

        # When
        retrieved_records = CoreTimeSeries.objects.get_queryset().query_for_data(
            theme=public_record.metric.topic.sub_theme.theme.name,
            sub_theme=public_record.metric.topic.sub_theme.name,
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            date_from="2020-01-01",
            date_to="2025-12-31",
            permission_sets=permission_sets,
        )

        # Then
        assert public_record in retrieved_records
        assert non_public_record in retrieved_records

    @pytest.mark.django_db
    @pytest.mark.parametrize("does_permission_match", [True, False])
    def test_query_for_data_method_handles_specific_permission_sets(
        self,
        does_permission_match: bool,
    ):
        """
        Given a public and a non-public CoreTimeSeries record
        When query_for_data() is called with a specific permission set
        Then the non-public record is only returned when the permission row matches
        """

        # Given
        public_record = CoreTimeSeriesFactory.create_record(
            metric_value=1,
            date="2020-01-01",
            is_public=True,
        )
        non_public_record = CoreTimeSeriesFactory.create_record(
            metric_value=2,
            date="2020-01-01",
            is_public=False,
        )
        permission_sets = {
            "permission_sets": [
                {
                    "theme": {
                        "id": str(non_public_record.metric.topic.sub_theme.theme.id)
                    },
                    "sub_theme": {
                        "id": str(non_public_record.metric.topic.sub_theme.id)
                    },
                    "topic": {"id": str(non_public_record.metric.topic.id)},
                    "metric": {
                        "id": str(
                            # Tweak id to be wrong for the negative test
                            non_public_record.metric.id
                            if does_permission_match
                            else 999999
                        )
                    },
                    "geography_type": {
                        "id": str(non_public_record.geography.geography_type.id)
                    },
                    "geography": {
                        "id": str(non_public_record.geography.geography_code)
                    },
                }
            ],
            "summary": {"has_global_access": False},
        }

        # When
        retrieved_records = CoreTimeSeries.objects.get_queryset().query_for_data(
            theme=public_record.metric.topic.sub_theme.theme.name,
            sub_theme=public_record.metric.topic.sub_theme.name,
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            geography=public_record.geography.name,
            geography_type=public_record.geography.geography_type.name,
            date_from="2010-01-01",
            date_to="2030-01-01",
            fields_to_export=[],
            permission_sets=permission_sets,
        )

        # Then
        assert public_record in retrieved_records
        assert (non_public_record in retrieved_records) is does_permission_match


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
    @mock.patch(
        "metrics.api.settings.auth.ENFORCE_PUBLIC_DATA_ONLY",
        True,
    )
    def test_get_available_geographies(self):
        """
        Given a `topic` and a number of public and non-public `CoreTimeSeries` records
        When `get_available_geographies()` is called
            from an instance of the `CoreTimeSeriesManager`
        Then only public geographies for the topic are returned
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
            geography_type_name="Nation",
            geography_name="Scotland",
            topic_name=topic,
            is_public=False,
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
    @mock.patch(
        "metrics.api.permissions.fluent_permissions.auth.ENFORCE_PUBLIC_DATA_ONLY",
        False,
    )
    def test_query_for_data_returns_non_public_record_with_global_permissions(self):
        """
        Given public and non-public `CoreTimeSeries` records
        And global JWT permission sets
        And `ENFORCE_PUBLIC_DATA_ONLY` is disabled
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

        params = {
            "theme": public_record.metric.topic.sub_theme.theme.name,
            "sub_theme": public_record.metric.topic.sub_theme.name,
            "topic": public_record.metric.topic.name,
            "metric": public_record.metric.name,
            "geography": public_record.geography.name,
            "geography_type": public_record.geography.geography_type.name,
        }
        permission_sets = {
            "permission_sets": [],
            "summary": {"has_global_access": True},
        }

        # When
        core_time_series_queryset = CoreTimeSeries.objects.query_for_data(
            **params,
            date_from="2020-01-01",
            date_to="2025-12-31",
            fields_to_export=[],
            permission_sets=permission_sets,
        )

        # Then
        assert public_record in core_time_series_queryset
        assert non_public_record in core_time_series_queryset

    @pytest.mark.django_db
    def test_query_for_data_excludes_non_public_record_without_permission_sets(self):
        """
        Given public and non-public `CoreTimeSeries` records
        And no permission sets are provided
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
        # When
        core_time_series_queryset = CoreTimeSeries.objects.query_for_data(
            theme=public_record.metric.topic.sub_theme.theme.name,
            sub_theme=public_record.metric.topic.sub_theme.name,
            topic=public_record.metric.topic.name,
            metric=public_record.metric.name,
            geography=public_record.geography.name,
            geography_type=public_record.geography.geography_type.name,
            fields_to_export=[],
            date_from="2020-01-01",
            date_to="2025-12-31",
        )

        # Then
        assert public_record in core_time_series_queryset
        assert non_public_record not in core_time_series_queryset

    @pytest.mark.django_db
    def test_query_for_data_excludes_out_of_range_record(self):
        """
        Given 3 CoreTimeSeries` records which are within range
        And 1 `CoreTimeSeries` which sits outside the given range
        When `query_for_data()` is called from the `CoreTimeSeriesManager`
        Then the out of range record is excluded
        """
        # Given
        in_range_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-01", metric_value=1, is_public=True
        )
        second_in_range_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-02", metric_value=2, is_public=True
        )
        third_in_range_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-02", metric_value=7, is_public=True
        )
        out_of_range_record = CoreTimeSeriesFactory.create_record(
            date="2023-01-03", metric_value=11, is_public=True
        )

        # When
        core_time_series_queryset = CoreTimeSeries.objects.query_for_data(
            theme=in_range_record.metric.topic.sub_theme.theme.name,
            sub_theme=in_range_record.metric.topic.sub_theme.name,
            topic=in_range_record.metric.topic.name,
            metric=in_range_record.metric.name,
            geography=in_range_record.geography.name,
            geography_type=in_range_record.geography.geography_type.name,
            date_from="2020-01-01",
            date_to="2025-12-31",
            metric_value_ranges=[(0, 5), (6, 9)],
        )

        # Then
        assert in_range_record in core_time_series_queryset
        assert second_in_range_record in core_time_series_queryset
        assert third_in_range_record in core_time_series_queryset
        assert out_of_range_record not in core_time_series_queryset


class TestFilterGeographiesByPermission:
    @pytest.fixture(autouse=True)
    def _enable_auth_and_silence_logging(self):
        with (
            mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", True),
            mock.patch(f"{MODULE_PATH}.log_user_permission_summary"),
        ):
            yield

    @staticmethod
    def _build_request(*, permission_sets=None, has_global_access=False):
        request = mock.Mock()
        request.auth = "fake-token"
        request.user.permission_sets = {
            "permission_sets": permission_sets or [],
            "summary": {"has_global_access": has_global_access},
        }
        return request

    @staticmethod
    def _build_data() -> list[dict]:
        return [
            {
                "geography_type": "Nation",
                "geographies": [{"name": "England"}, {"name": "Scotland"}],
            },
            {
                "geography_type": "Lower Tier Local Authority",
                "geographies": [{"name": "Hackney"}],
            },
        ]

    def test_returns_data_unchanged_when_auth_is_disabled(self):
        """
        Given `AUTH_ENABLED` is False
        When `filter_geographies_by_permission()` is called
        Then the data is returned untouched
        """
        # Given
        data = self._build_data()
        request = self._build_request()

        # When
        with mock.patch(f"{MODULE_PATH}.AUTH_ENABLED", False):
            filtered = filter_geographies_by_permission(
                request=request,
                data=data,
                theme="infectious_disease",
                sub_theme="respiratory",
                topic="",
            )

        # Then
        assert filtered == data

    @pytest.mark.parametrize("missing", ["request", "auth"])
    def test_returns_data_unchanged_for_unauthenticated_requests(self, missing: str):
        """
        Given a missing request or a request with no `auth`
        When `filter_geographies_by_permission()` is called
        Then the data is returned untouched
        """
        # Given
        data = self._build_data()
        request = None
        if missing == "auth":
            request = self._build_request()
            request.auth = None

        # When
        filtered = filter_geographies_by_permission(
            request=request,
            data=data,
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="",
        )

        # Then
        assert filtered == data

    @mock.patch(f"{MODULE_PATH}.MetricsAPIInterface")
    def test_returns_data_unchanged_for_global_access(
        self, spy_metrics_api_interface: mock.MagicMock
    ):
        """
        Given a user with global access
        When `filter_geographies_by_permission()` is called
        Then the data is returned untouched
        And no id lookups are performed
        """
        # Given
        data = self._build_data()
        request = self._build_request(has_global_access=True)

        # When
        filtered = filter_geographies_by_permission(
            request=request,
            data=data,
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="",
        )

        # Then
        assert filtered == data
        spy_metrics_api_interface.get_topic_manager.assert_not_called()

    @mock.patch(f"{MODULE_PATH}._is_geography_permitted")
    @mock.patch(f"{MODULE_PATH}.MetricsAPIInterface")
    def test_filters_geographies_for_each_geography_type_without_topic(
        self,
        spy_metrics_api_interface: mock.MagicMock,
        spy_is_geography_permitted: mock.MagicMock,
    ):
        """
        Given a user without global access
        And data containing multiple geography types
        When `filter_geographies_by_permission()` is called without a `topic`
        Then only the permitted geographies are returned for every geography type
        And geography types with no permitted geographies are dropped
        """
        # Given
        spy_metrics_api_interface.get_theme_manager.return_value.get_id_by_name.return_value = (
            1
        )
        spy_metrics_api_interface.get_sub_theme_manager.return_value.get_id_by_name.return_value = (
            2
        )
        spy_metrics_api_interface.get_geography_type_manager.return_value.get_id_by_name.return_value = (
            4
        )
        spy_is_geography_permitted.side_effect = (
            lambda **kwargs: kwargs["geography_name"] == "England"
        )
        request = self._build_request(permission_sets=[{"fake": "permission set"}])

        # When
        filtered = filter_geographies_by_permission(
            request=request,
            data=self._build_data(),
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="",
        )

        # Then
        assert filtered == [
            {"geography_type": "Nation", "geographies": [{"name": "England"}]}
        ]

    @mock.patch(f"{MODULE_PATH}._is_geography_permitted")
    @mock.patch(f"{MODULE_PATH}.MetricsAPIInterface")
    def test_keeps_all_permitted_geography_types(
        self,
        spy_metrics_api_interface: mock.MagicMock,
        spy_is_geography_permitted: mock.MagicMock,
    ):
        """
        Given a user who is permitted to see every geography
        When `filter_geographies_by_permission()` is called
        Then every geography type is retained in the output
        """
        # Given
        spy_metrics_api_interface.get_theme_manager.return_value.get_id_by_name.return_value = (
            1
        )
        spy_metrics_api_interface.get_sub_theme_manager.return_value.get_id_by_name.return_value = (
            2
        )
        spy_metrics_api_interface.get_geography_type_manager.return_value.get_id_by_name.return_value = (
            4
        )
        spy_is_geography_permitted.return_value = True
        data = self._build_data()
        request = self._build_request(permission_sets=[{"fake": "permission set"}])

        # When
        filtered = filter_geographies_by_permission(
            request=request,
            data=data,
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="",
        )

        # Then
        assert filtered == data

    @mock.patch(f"{MODULE_PATH}._is_geography_permitted")
    @mock.patch(f"{MODULE_PATH}.MetricsAPIInterface")
    def test_resolves_ids_from_topic_when_topic_provided(
        self,
        spy_metrics_api_interface: mock.MagicMock,
        spy_is_geography_permitted: mock.MagicMock,
    ):
        """
        Given a `topic` is provided
        When `filter_geographies_by_permission()` is called
        Then the theme, sub theme and topic ids are resolved via the topic manager
        And these ids are passed through to the permission check
        """
        # Given
        spy_topic_manager = spy_metrics_api_interface.get_topic_manager.return_value
        spy_topic_manager.get_id_by_name.return_value = (1, 2, 3)
        spy_metrics_api_interface.get_geography_type_manager.return_value.get_id_by_name.return_value = (
            4
        )
        spy_is_geography_permitted.return_value = True
        data = [{"geography_type": "Nation", "geographies": [{"name": "England"}]}]
        request = self._build_request(permission_sets=[{"fake": "permission set"}])

        # When
        filtered = filter_geographies_by_permission(
            request=request,
            data=data,
            theme="infectious_disease",
            sub_theme="respiratory",
            topic="COVID-19",
        )

        # Then
        spy_topic_manager.get_id_by_name.assert_called_once_with(
            "infectious_disease", "respiratory", "COVID-19"
        )
        _, kwargs = spy_is_geography_permitted.call_args
        assert kwargs["theme_id"] == 1
        assert kwargs["sub_theme_id"] == 2
        assert kwargs["topic_id"] == 3
        assert filtered == data


class TestIsGeographyPermitted:
    THEME_ID = 1
    SUB_THEME_ID = 2
    TOPIC_ID = 3
    GEOGRAPHY_TYPE_ID = 4
    GEOGRAPHY_CODE = "E92000001"

    @classmethod
    def _build_permission_set(cls, **overrides) -> dict:
        ids = {
            "theme": str(cls.THEME_ID),
            "sub_theme": str(cls.SUB_THEME_ID),
            "topic": str(cls.TOPIC_ID),
            "geography_type": str(cls.GEOGRAPHY_TYPE_ID),
            "geography": cls.GEOGRAPHY_CODE,
        }
        ids.update(overrides)
        return {field: {"id": value} for field, value in ids.items()}

    @classmethod
    def _call(cls, *, permission_sets: list, geography_code="E92000001", **overrides):
        geography_manager = mock.Mock()
        geography_manager.get_code_by_name.return_value = geography_code

        kwargs = {
            "permission_sets": permission_sets,
            "geography_type_id": cls.GEOGRAPHY_TYPE_ID,
            "geography_type_name": "Nation",
            "geography_name": "England",
            "geography_manager": geography_manager,
            "theme_id": cls.THEME_ID,
            "sub_theme_id": cls.SUB_THEME_ID,
            "topic_id": cls.TOPIC_ID,
        }
        kwargs.update(overrides)
        return _is_geography_permitted(**kwargs)

    def test_returns_true_when_permission_set_matches(self):
        """
        Given a permission set matching the theme, sub theme, topic and geography
        When `_is_geography_permitted()` is called
        Then True is returned
        """
        # Given
        permission_sets = [self._build_permission_set()]

        # When / Then
        assert self._call(permission_sets=permission_sets) is True

    def test_returns_false_when_there_are_no_permission_sets(self):
        """
        Given no permission sets
        When `_is_geography_permitted()` is called
        Then False is returned
        """
        assert self._call(permission_sets=[]) is False

    @pytest.mark.parametrize(
        "mismatched_field",
        ["theme", "sub_theme", "topic", "geography_type", "geography"],
    )
    def test_returns_false_when_a_permission_field_does_not_match(
        self, mismatched_field: str
    ):
        """
        Given a permission set where 1 of the fields does not match the request
        When `_is_geography_permitted()` is called
        Then False is returned
        """
        # Given
        permission_sets = [self._build_permission_set(**{mismatched_field: "999999"})]

        # When / Then
        assert self._call(permission_sets=permission_sets) is False

    def test_returns_true_when_any_one_permission_set_matches(self):
        """
        Given a non-matching permission set and a matching one
        When `_is_geography_permitted()` is called
        Then True is returned
        """
        # Given
        permission_sets = [
            self._build_permission_set(geography="999999"),
            self._build_permission_set(),
        ]

        # When / Then
        assert self._call(permission_sets=permission_sets) is True

    def test_ignores_permission_sets_which_are_not_dicts(self):
        """
        Given a malformed permission set alongside a matching one
        When `_is_geography_permitted()` is called
        Then the malformed entry is skipped and True is returned
        """
        # Given
        permission_sets = ["not-a-dict", None, self._build_permission_set()]

        # When / Then
        assert self._call(permission_sets=permission_sets) is True

    def test_ignores_permission_sets_without_a_geography_type(self):
        """
        Given a permission set which has no geography type
        When `_is_geography_permitted()` is called
        Then False is returned
        """
        # Given
        permission_set = self._build_permission_set()
        del permission_set["geography_type"]

        # When / Then
        assert self._call(permission_sets=[permission_set]) is False

    @pytest.mark.parametrize(
        "overrides",
        [
            {"geography_type_id": None},
            {"theme_id": None},
            {"sub_theme_id": None},
        ],
    )
    def test_returns_false_when_a_required_id_is_missing(self, overrides: dict):
        """
        Given a matching permission set
        But a required theme, sub theme or geography type id could not be resolved
        When `_is_geography_permitted()` is called
        Then False is returned
        """
        # Given
        permission_sets = [self._build_permission_set()]

        # When / Then
        assert self._call(permission_sets=permission_sets, **overrides) is False

    def test_returns_false_when_geography_code_cannot_be_resolved(self):
        """
        Given a matching permission set
        But the geography manager cannot find a code for the geography
        When `_is_geography_permitted()` is called
        Then False is returned
        """
        # Given
        permission_sets = [self._build_permission_set()]

        # When / Then
        assert self._call(permission_sets=permission_sets, geography_code=None) is False
