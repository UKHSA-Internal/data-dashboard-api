import unittest
from unittest import mock

from metrics.data.managers.core_models.sub_theme import (
    SubThemeManager,
    SubThemeQuerySet,
)


class TestSubThemeManager:
    @mock.patch.object(SubThemeQuerySet, "get_all_names")
    def test_get_all_sub_theme_names(self, spy_get_all_names: mock.MagicMock):
        """
        Given an instance of a `SubThemeManager`
        When `get_all_names` is called
        Then it delegates call to `SubThemeQuerySet`.
        """
        # Given
        sub_theme_manager = SubThemeManager()

        # When
        sub_theme_manager.get_all_names()

        # Then
        spy_get_all_names.assert_called_once_with()
