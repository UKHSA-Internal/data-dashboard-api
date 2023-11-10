import datetime

import pytest
from django.utils import timezone

from metrics.data.models.core_models import CoreHeadline
from tests.factories.metrics.headline import CoreHeadlineFactory


class TestCoreHeadlineManager:
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
        retrieved_record = CoreHeadline.objects.get_latest_metric_value(
            topic_name=expected_round_headline.metric.topic.name,
            metric_name=expected_round_headline.metric.name,
            geography_name=expected_round_headline.geography.name,
            geography_type_name=expected_round_headline.geography.geography_type.name,
        )

        # Then
        assert (
            retrieved_record
            == expected_round_headline.metric_value
            != second_stale_round_headline.metric_value
            != first_stale_round_headline.metric_value
        )

    @pytest.mark.django_db
    def test_embargoed_data_is_not_returned_in_query(self):
        """
        Given a `CoreHeadline` record which is considered to be live
        And another `CoreHeadline` record is under embargo
        When `by_topic_metric_ordered_from_newest_to_oldest()` is called
            from an instance of the `CoreHeadlineQuerySet`
        Then the 'live' record is returned without the data under embargo
        """
        # Given
        original_metric_value = 99
        core_headline_live = CoreHeadlineFactory.create_record(
            metric_value=original_metric_value
        )

        current_date = timezone.now()
        future_embargo_date = datetime.datetime(
            year=current_date.year + 1,
            month=current_date.month,
            day=current_date.day,
        )
        embargoed_metric_value = 100
        core_headline_under_embargo = CoreHeadlineFactory.create_record(
            metric_value=embargoed_metric_value, embargo=future_embargo_date
        )

        # When
        core_headline_queryset = CoreHeadline.objects.get_queryset()
        returned_queryset = (
            core_headline_queryset.by_topic_metric_ordered_from_newest_to_oldest(
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
        assert core_headline_live.metric_value in returned_queryset
        assert core_headline_under_embargo.metric_value not in returned_queryset

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
