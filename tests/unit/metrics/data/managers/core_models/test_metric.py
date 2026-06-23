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
    def test_get_all_unique_names(
        self, spy_get_all_unique_names: mock.MagicMock
    ):
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
