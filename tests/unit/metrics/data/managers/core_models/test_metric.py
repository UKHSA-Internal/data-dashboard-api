import unittest
from unittest import mock

from metrics.data.managers.core_models.metric import (
    MetricManager,
    MetricQuerySet,
)


class TestMetricManager(unittest.TestCase):
    @mock.patch.object(MetricQuerySet, "get_all_names_and_ids")
    def test_get_all_theme_names_and_ids(
        self, spy_get_all_names_and_ids: mock.MagicMock
    ):
        """
        Given an instance of a `metricManager`
        When `get_all_names` is called
        Then it delegates call to `MetricQuerySet`.
        """
        # Given
        metric_manager = MetricManager()

        # When
        metric_manager.get_all_names_and_ids()

        # Then
        spy_get_all_names_and_ids.assert_called_once()

    @mock.patch.object(MetricQuerySet, "get_all_unique_names")
    def test_get_all_unique_names(self, spy_get_all_unique_names: mock.MagicMock):
        """
        Given an instance of a `metricManager`
        When `get_all_unique_names` is called
        Then it delegates call to `MetricQuerySet`.
        """
        # Given
        metric_manager = MetricManager()

        # When
        metric_manager.get_all_unique_names()

        # Then
        spy_get_all_unique_names.assert_called_once()


class TestMetricQuerySet(unittest.TestCase):
    def test_get_filtered_unique_names_related_to_parent_topic_id_filters_off_sens_when_not_public(
        self,
    ):
        """
        Given a MetricQuerySet and is_public set to False
        When metrics are filtered by topic id
        Then only OFF-SENS metrics are requested from the queryset
        """
        # Given
        queryset = MetricQuerySet(model=mock.MagicMock())

        filtered_queryset = mock.MagicMock()
        filtered_queryset.values.return_value.distinct.return_value = []

        with (
            mock.patch.object(
                MetricQuerySet,
                "filter",
                return_value=filtered_queryset,
            ) as spy_filter,
        ):
            # When
            queryset.get_filtered_unique_names_related_to_parent_topic_id(
                1,
                is_public=False,
            )

        # Then
        spy_filter.assert_any_call(topic_id=1)
        filtered_queryset.filter.assert_called_once_with(name__startswith="OFF-SENS")

    def test_get_filtered_unique_names_related_to_parent_topic_id_excludes_off_sens_when_public(
        self,
    ):
        """
        Given a MetricQuerySet and is_public set to True
        When metrics are filtered by topic id
        Then OFF-SENS metrics are excluded from the queryset
        """
        # Given
        queryset = MetricQuerySet(model=mock.MagicMock())

        filtered_queryset = mock.MagicMock()
        filtered_queryset.exclude.return_value = filtered_queryset
        filtered_queryset.values.return_value.distinct.return_value = []

        with (
            mock.patch.object(
                MetricQuerySet,
                "filter",
                return_value=filtered_queryset,
            ) as spy_filter,
        ):
            # When
            queryset.get_filtered_unique_names_related_to_parent_topic_id(
                1,
                is_public=True,
            )

        # Then
        spy_filter.assert_any_call(topic_id=1)
        filtered_queryset.exclude.assert_called_once_with(name__startswith="OFF-SENS")
