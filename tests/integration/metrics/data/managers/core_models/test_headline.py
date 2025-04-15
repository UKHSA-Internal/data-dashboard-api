import datetime

import pytest
from django.utils import timezone

from metrics.data.models.core_models import CoreHeadline
from metrics.domain.models import get_date_n_months_ago_from_timestamp
from tests.factories.metrics.headline import CoreHeadlineFactory


class TestCoreHeadlineManager:

    @pytest.mark.django_db
    def test_query_for_data_returns_expected_results(
        self,
    ):
        """
        Given a `CoreHeadline` record is live
        When `query_for_data()` is called
        Then then a queryset is returned with the correct x and y values
            and the `period_end` of the record is added to the queryset as
            `latest_date`
        """
        # Given
        expected_record_period_start = "2024-01-01"
        expected_record_period_end = "2024-01-02"
        expected_record_headline = CoreHeadlineFactory.create_record(
            metric_value=3,
            period_start=expected_record_period_start,
            period_end=expected_record_period_end,
        )

        # When
        retrieved_record_queryset = CoreHeadline.objects.query_for_data(
            fields_to_export=["age", "metric_value"],
            topic_name=expected_record_headline.metric.topic.name,
            metric_name=expected_record_headline.metric.name,
            geography_name=expected_record_headline.geography.name,
        )

        retrieved_record_values = retrieved_record_queryset.values(
            "age", "metric_value"
        )

        # Then
        assert len(retrieved_record_queryset[0]) == 2
        assert (
            retrieved_record_queryset[0]["metric_value"]
            == retrieved_record_values[0]["metric_value"]
        )
        assert retrieved_record_queryset[0]["age"] == retrieved_record_values[0]["age"]
        assert (
            retrieved_record_queryset.latest_date.strftime("%Y-%m-%d")
            == expected_record_period_end
        )

    @pytest.mark.django_db
    def test_get_latest_metric_value_returns_latest_metric_value_for_multiple_versions(
        self,
    ):
        """
        Given a number of `CoreHeadline` records which are stale
        And a `CoreHeadline` records which is live
        When `get_latest_metric_value()` is called
            from an instance of the `CoreHeadlineManager`
        Then only the metric_value associated
            with the latest `CoreHeadline` record is returned
        """
        # Given
        first_stale_round_outdated_period_start = "2023-01-01"
        first_stale_round_outdated_period_end = "2023-01-02"
        first_stale_round_headline = CoreHeadlineFactory.create_record(
            metric_value=1,
            period_start=first_stale_round_outdated_period_start,
            period_end=first_stale_round_outdated_period_end,
        )

        second_stale_round_outdated_period_start = "2023-01-03"
        second_stale_round_outdated_period_end = "2023-01-04"
        second_stale_round_headline = CoreHeadlineFactory.create_record(
            metric_value=2,
            period_start=second_stale_round_outdated_period_start,
            period_end=second_stale_round_outdated_period_end,
        )

        expected_round_outdated_period_start = "2023-01-05"
        expected_round_outdated_period_end = "2023-01-06"
        expected_round_headline = CoreHeadlineFactory.create_record(
            metric_value=3,
            period_start=expected_round_outdated_period_start,
            period_end=expected_round_outdated_period_end,
        )

        # When
        retrieved_record = CoreHeadline.objects.get_latest_headline(
            topic_name=expected_round_headline.metric.topic.name,
            metric_name=expected_round_headline.metric.name,
            geography_name=expected_round_headline.geography.name,
            geography_type_name=expected_round_headline.geography.geography_type.name,
        )

        # Then
        assert (
            retrieved_record.metric_value
            == expected_round_headline.metric_value
            != second_stale_round_headline.metric_value
            != first_stale_round_headline.metric_value
        )

    @pytest.mark.django_db
    def test_embargoed_data_is_not_returned_in_query(self):
        """
        Given a `CoreHeadline` record which is considered to be live
        And another `CoreHeadline` record is under embargo
        When `get_all_headlines_released_from_embargo()` is called
            from an instance of the `CoreHeadlineQuerySet`
        Then the 'live' record is returned without the data under embargo
        """
        # Given
        original_metric_value = 99
        core_headline_live = CoreHeadlineFactory.create_record(
            metric_value=original_metric_value
        )

        current_date = timezone.now()
        future_embargo_date = get_date_n_months_ago_from_timestamp(
            datetime_stamp=current_date,
            number_of_months=-2,
        )
        embargoed_metric_value = 100
        core_headline_under_embargo = CoreHeadlineFactory.create_record(
            metric_value=embargoed_metric_value, embargo=future_embargo_date
        )

        # When
        core_headline_queryset = CoreHeadline.objects.get_queryset()
        returned_queryset = (
            core_headline_queryset.get_all_headlines_released_from_embargo(
                topic_name=core_headline_live.metric.topic.name,
                metric_name=core_headline_live.metric.name,
                geography_name=core_headline_live.geography.name,
                geography_type_name=core_headline_live.geography.geography_type.name,
                stratum_name=core_headline_live.stratum.name,
                sex=core_headline_live.sex,
                age=core_headline_live.age.name,
            )
        )

        # Then
        returned_metric_values = returned_queryset.values_list(
            "metric_value", flat=True
        )
        assert core_headline_live.metric_value in returned_metric_values
        assert core_headline_under_embargo.metric_value not in returned_metric_values

    @pytest.mark.django_db
    def test_data_with_no_embargo_set_is_returned(self):
        """
        Given a `CoreHeadline` record which is considered to be live
        And another `CoreHeadline` record has been
            designated to be immediately queryable with a `None` embargo value
        When `by_topic_metric_ordered_from_newest_to_oldest()` is called
            from an instance of the `CoreHeadlineQuerySet`
        Then the record returned is the record which
            had an immediately queryable embargo value of `None`
        """
        # Given
        original_metric_value = 99
        original_refresh_date = datetime.datetime(year=2023, month=11, day=1)
        core_headline_live = CoreHeadlineFactory.create_record(
            metric_value=original_metric_value,
            refresh_date=original_refresh_date,
        )

        updated_refresh_date = datetime.datetime(year=2023, month=11, day=8)
        embargoed_metric_value = 100
        core_headline_with_immediate_embargo = CoreHeadlineFactory.create_record(
            metric_value=embargoed_metric_value,
            embargo=None,
            refresh_date=updated_refresh_date,
        )

        # When
        core_headline = CoreHeadline.objects.get_latest_headline(
            topic_name=core_headline_live.metric.topic.name,
            metric_name=core_headline_live.metric.name,
            geography_name=core_headline_live.geography.name,
            geography_type_name=core_headline_live.geography.geography_type.name,
            stratum_name=core_headline_live.stratum.name,
            sex=core_headline_live.sex,
            age=core_headline_live.age.name,
        )

        # Then
        assert (
            core_headline.metric_value
            == core_headline_with_immediate_embargo.metric_value
        )

    @pytest.mark.django_db
    def test_exclude_data_under_embargo(self):
        """
        Given a `CoreHeadline` records which is live
        And a `CoreHeadline` record which is under embargo
        When `_exclude_data_under_embargo()` is called
            from an instance of  `CoreHeadlineQueryset`
        Then only the live `CoreHeadline` record is returned
        """
        # Given
        current_time = timezone.now()
        live_core_headline = CoreHeadlineFactory.create_record(
            metric_value=123, embargo=current_time - datetime.timedelta(days=7)
        )

        embargo_point_in_time = current_time + datetime.timedelta(days=7)
        embargoed_core_headline = CoreHeadlineFactory.create_record(
            metric_value=456, embargo=embargo_point_in_time
        )

        # When
        input_queryset = CoreHeadline.objects.get_queryset()
        filtered_queryset = input_queryset._exclude_data_under_embargo(
            queryset=input_queryset
        )

        # Then
        # The live record should be in the returned queryset
        assert live_core_headline in filtered_queryset

        # The embargoed record should not be in the returned queryset
        assert embargoed_core_headline not in filtered_queryset

    @pytest.mark.django_db
    def test_get_latest_headline_with_current_period_end(self):
        """
        Given a `CoreHeadline` record which has `period_end` of 1 week ago
        And a `CoreHeadline` record which has `period_end` of 1 week forwards from now
        When `get_latest_headline()` is called
            from an instance of  `CoreHeadlineManager`
        Then the record with the `period_end` which is in the future is returned
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "COVID-19_headline_7DayAdmissions"
        geography_code = "E92000001"
        current_time = timezone.now()

        # Expired record
        expired_period_end = current_time - datetime.timedelta(days=7)
        expired_core_headline = CoreHeadlineFactory.create_record(
            metric_value=123,
            embargo=None,
            geography_code=geography_code,
            period_end=expired_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )

        # Record which is not expired but has been superseded
        valid_but_superseded_period_end = current_time + datetime.timedelta(days=3)
        superseded_core_headline = CoreHeadlineFactory.create_record(
            metric_value=456,
            embargo=None,
            geography_code=geography_code,
            period_end=valid_but_superseded_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )

        # Record which is currently valid
        currently_valid_period_end = current_time + datetime.timedelta(days=7)
        current_core_headline = CoreHeadlineFactory.create_record(
            metric_value=789,
            embargo=None,
            geography_code=geography_code,
            period_end=currently_valid_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )

        # When
        result = CoreHeadline.objects.get_latest_headline(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_code=geography_code,
        )

        # Then
        # ----------------------------
        # | record |   period_end    |
        # ----------------------------
        # |    A   | 7 days ago      |
        # |    B   | 3 days from now |
        # |    C   | 7 days from now |
        # ----------------------------
        # In this case, record C should be returned
        assert (
            result
            == current_core_headline
            != expired_core_headline
            != superseded_core_headline
        )

    @pytest.mark.django_db
    def test_get_latest_headlines_for_geography_codes(self):
        """
        Given a `CoreHeadline` record which has `period_end` of 1 week ago
        And a `CoreHeadline` record which has `period_end` of 1 week forwards from now
            for multiple different geographies
        When `get_latest_headlines_for_geography_codes()` is called
            from an instance of  `CoreHeadlineManager`
        Then the record with the `period_end` which is in the future is returned
            for each individual geography code
        """
        # Given
        topic_name = "COVID-19"
        metric_name = "COVID-19_headline_7DayAdmissions"
        current_time = timezone.now()

        first_geography_code = "E08000033"
        # Expired record for 1st geography
        expired_period_end = current_time - datetime.timedelta(days=7)
        expired_core_headline_for_first_geography = CoreHeadlineFactory.create_record(
            metric_value=123,
            embargo=None,
            geography_code=first_geography_code,
            period_end=expired_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )
        # Record which is currently valid for 1st geography
        currently_valid_period_end = current_time + datetime.timedelta(days=7)
        current_core_headline_for_first_geography = CoreHeadlineFactory.create_record(
            metric_value=456,
            embargo=None,
            geography_code=first_geography_code,
            period_end=currently_valid_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )
        # Expired record for 2nd geography
        second_geography_code = "E92000002"
        expired_period_end = current_time - datetime.timedelta(days=6)
        expired_core_headline_for_second_geography = CoreHeadlineFactory.create_record(
            metric_value=111,
            embargo=None,
            geography_name="West Midlands",
            geography_type_name="",
            geography_code=second_geography_code,
            period_end=expired_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )
        # Record which is currently valid for 2nd geography
        currently_valid_period_end = current_time + datetime.timedelta(days=5)
        current_core_headline_for_second_geography = CoreHeadlineFactory.create_record(
            metric_value=222,
            embargo=None,
            geography_name="West Midlands",
            geography_type_name="",
            geography_code=second_geography_code,
            period_end=currently_valid_period_end,
            topic_name=topic_name,
            metric_name=metric_name,
        )

        # When
        result = CoreHeadline.objects.get_latest_headlines_for_geography_codes(
            topic_name=topic_name,
            metric_name=metric_name,
            geography_codes=[first_geography_code, second_geography_code],
        )

        # Then
        assert result == {
            first_geography_code: current_core_headline_for_first_geography,
            second_geography_code: current_core_headline_for_second_geography,
        }
        assert (
            result[first_geography_code]
            == current_core_headline_for_first_geography
            != expired_core_headline_for_first_geography
        )
        assert (
            result[second_geography_code]
            == current_core_headline_for_second_geography
            != expired_core_headline_for_second_geography
        )

    @pytest.mark.django_db
    def test_delete_superseded_data_deletes_stale_records_only(
        self, timestamp_2_months_from_now: datetime.datetime
    ):
        """
        Given a number of `CoreHeadline` records which are stale
        And a `CoreHeadline` records which is live
        And a `CoreHeadline` records which is under embargo
        When `delete_superseded_data()` is called
            from an instance of the `CoreHeadlineManager`
        Then only the stale records are deleted
        And the live & embargoed records are still available
        """
        # Given
        first_stale_round_outdated_period_start = "2023-01-01"
        first_stale_round_outdated_period_end = "2023-01-02"
        first_stale_round_headline = CoreHeadlineFactory.create_record(
            metric_value=1,
            period_start=first_stale_round_outdated_period_start,
            period_end=first_stale_round_outdated_period_end,
        )

        second_stale_round_outdated_period_start = "2023-01-03"
        second_stale_round_outdated_period_end = "2023-01-04"
        second_stale_round_headline = CoreHeadlineFactory.create_record(
            metric_value=2,
            period_start=second_stale_round_outdated_period_start,
            period_end=second_stale_round_outdated_period_end,
        )

        current_round_period_start = "2023-01-05"
        current_round_period_end = "2023-01-06"
        current_round_headline = CoreHeadlineFactory.create_record(
            metric_value=3,
            period_start=current_round_period_start,
            period_end=current_round_period_end,
        )

        embargoed_round_period_start = "2023-01-07"
        embargoed_round_period_end = "2023-01-10"
        embargoed_round_headline = CoreHeadlineFactory.create_record(
            metric_value=4,
            period_start=embargoed_round_period_start,
            period_end=embargoed_round_period_end,
            embargo=timestamp_2_months_from_now,
        )

        # When
        CoreHeadline.objects.delete_superseded_data(
            topic_name=current_round_headline.metric.topic.name,
            metric_name=current_round_headline.metric.name,
            geography_name=current_round_headline.geography.name,
            geography_code=current_round_headline.geography.geography_code,
            geography_type_name=current_round_headline.geography.geography_type.name,
            stratum_name=current_round_headline.stratum.name,
            age=current_round_headline.age.name,
            sex=current_round_headline.sex,
            is_public=current_round_headline.is_public,
        )
        retrieved_records = CoreHeadline.objects.all()

        # Then
        assert first_stale_round_headline not in retrieved_records
        assert second_stale_round_headline not in retrieved_records
        assert current_round_headline in retrieved_records
        assert embargoed_round_headline in retrieved_records

    @pytest.mark.django_db
    def test_find_latest_released_embargo_for_metrics(self):
        """
        Given a number of `CoreHeadline` records
            for different metrics
        When `find_latest_released_embargo_for_metrics()` is called
            from an instance of the `CoreHeadlineManager`
        Then the latest released embargo timestamp is returned
        """
        # Given
        covid_metric = "COVID-19_headline_7DayAdmissions"
        covid_metric_for_outdated_embargo = "COVID-19_headline_7DayOccupiedBeds"

        superseded_embargo = datetime.datetime(
            year=2024, month=1, day=1, hour=1, minute=1, second=1, tzinfo=datetime.UTC
        )
        latest_released_embargo = datetime.datetime(
            year=2024, month=2, day=2, hour=1, minute=2, second=2, tzinfo=datetime.UTC
        )
        last_unreleased_embargo = get_date_n_months_ago_from_timestamp(
            datetime_stamp=timezone.now(), number_of_months=-1
        )

        CoreHeadlineFactory.create_record(
            metric_name=covid_metric, embargo=latest_released_embargo
        )
        CoreHeadlineFactory.create_record(
            metric_name=covid_metric_for_outdated_embargo, embargo=superseded_embargo
        )
        CoreHeadlineFactory.create_record(
            metric_name="adenovirus_headline_positivityLatest",
            embargo=last_unreleased_embargo,
        )

        # When
        extracted_embargo = (
            CoreHeadline.objects.find_latest_released_embargo_for_metrics(
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
        Given no existing `CoreHeadline` records
        When `find_latest_released_embargo_for_metrics()` is called
            from an instance of the `CoreHeadlineManager`
        Then None is returned
        """
        # Given
        covid_metric = "COVID-19_headline_7DayAdmissions"

        # When
        extracted_embargo = (
            CoreHeadline.objects.find_latest_released_embargo_for_metrics(
                metrics=[covid_metric]
            )
        )

        # Then
        assert extracted_embargo is None
