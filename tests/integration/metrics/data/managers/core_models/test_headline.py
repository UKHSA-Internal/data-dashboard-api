import pytest

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
