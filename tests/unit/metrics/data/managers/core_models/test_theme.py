import unittest
from unittest import mock

from metrics.data.managers.core_models.theme import (
    ThemeManager,
    ThemeQuerySet,
)


class TestThemeManager(unittest.TestCase):
    @mock.patch.object(ThemeQuerySet, "get_all_names")
    def test_get_all_theme_names(self, spy_get_all_names: mock.MagicMock):
        """
        Given an instance of a `ThemeManager`
        When `get_all_names` is called
        Then it delegates call to `ThemeQuerySet`.
        """
        # Given
        theme_manager = ThemeManager()

        # When
        theme_manager.get_all_names()

        # Then
        spy_get_all_names.assert_called_once()
