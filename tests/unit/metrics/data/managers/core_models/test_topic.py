import unittest
from unittest import mock

from metrics.data.managers.core_models.topic import (
    TopicManager,
    TopicQuerySet,
)


class TestThemeManager(unittest.TestCase):
    @mock.patch.object(TopicQuerySet, "get_all_names_and_ids")
    def test_get_all_theme_names_and_ids(
        self, spy_get_all_names_and_ids: mock.MagicMock
    ):
        """
        Given an instance of a `topicManager`
        When `get_all_names` is called
        Then it delegates call to `TopicQuerySet`.
        """
        # Given
        topic_manager = TopicManager()

        # When
        topic_manager.get_all_names_and_ids()

        # Then
        spy_get_all_names_and_ids.assert_called_once()
