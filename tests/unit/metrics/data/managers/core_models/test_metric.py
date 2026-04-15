import unittest
from unittest import mock

from metrics.data.managers.core_models.metric import (
    MetricManager,
    MetricQuerySet,
)


class TestThemeManager(unittest.TestCase):
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
