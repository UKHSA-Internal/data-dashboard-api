from unittest import mock

from metrics.data.managers.core_models.headline import (
    CoreHeadlineManager,
    CoreHeadlineQuerySet,
)
from metrics.data.models.core_models import CoreHeadline


class TestCoreHeadlineManager:
    @mock.patch.object(CoreHeadlineManager, "query_for_superseded_data")
    def test_delete_superseded_data(
        self, spy_query_for_superseded_data: mock.MagicMock
    ):
        """
        Given a payload containing the required fields
            for a dataset slice
        When `delete_superseded_data()` is called
            from an instance of the `CoreHeadlineManager`
        Then the records are retrieved via the
            call made to the `query_for_superseded_data()` method
        And then the retrieved records are deleted
        """
        # Given
        fake_topic = "COVID-19"
        fake_metric = "COVID-19_deaths_ONSByWeek"
        fake_geography = "England"
        fake_geography_type = "Nation"
        fake_geography_code = "E92000001"
        fake_stratum = "default"
        fake_sex = "all"
        fake_age = "all"
        fake_is_public = True

        # When
        CoreHeadlineManager().delete_superseded_data(
            topic=fake_topic,
            metric=fake_metric,
            geography=fake_geography,
            geography_type=fake_geography_type,
            geography_code=fake_geography_code,
            stratum=fake_stratum,
            sex=fake_sex,
            age=fake_age,
            is_public=fake_is_public,
        )

        # Then
        spy_query_for_superseded_data.assert_called_with(
            topic_name=fake_topic,
            metric_name=fake_metric,
            geography_name=fake_geography,
            geography_type_name=fake_geography_type,
            geography_code=fake_geography_code,
            stratum_name=fake_stratum,
            sex=fake_sex,
            age=fake_age,
            is_public=fake_is_public,
        )

        returned_records = spy_query_for_superseded_data.return_value
        returned_records.delete.assert_called_once()

    @mock.patch.object(
        CoreHeadlineQuerySet, "get_public_only_headlines_released_from_embargo"
    )
    def test_query_for_superseded_data_returns_empty_queryset_for_no_data(
        self, mocked_get_public_only_headlines_released_from_embargo: mock.MagicMock
    ):
        """
        Given a payload containing the required fields
            for a dataset slice which does not exist
        When `query_for_superseded_data()` is called
            from an instance of the `CoreHeadlineManager`
        Then an empty queryset is returned
        """
        # Given
        fake_topic = "COVID-19"
        fake_metric = "COVID-19_deaths_ONSByWeek"
        fake_geography = "England"
        fake_geography_type = "Nation"
        fake_geography_code = "E92000001"
        fake_stratum = "default"
        fake_sex = "all"
        fake_age = "all"
        mocked_get_public_only_headlines_released_from_embargo.return_value = (
            CoreHeadline.objects.none()
        )

        # When
        queryset = CoreHeadline.objects.query_for_superseded_data(
            topic_name=fake_topic,
            metric_name=fake_metric,
            geography_name=fake_geography,
            geography_type_name=fake_geography_type,
            geography_code=fake_geography_code,
            stratum_name=fake_stratum,
            sex=fake_sex,
            age=fake_age,
        )

        # Then
        assert not queryset.exists()
