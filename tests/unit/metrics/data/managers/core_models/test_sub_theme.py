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

    @mock.patch.object(SubThemeQuerySet, "get_all_unique_names")
    def test_get_all_unique_names(self, spy_get_all_unique_names: mock.MagicMock):
        """
        Given an instance of a `SubThemeManager`
        When `get_all_unique_names` is called
        Then it delegates call to `SubThemeQuerySet`.
        """
        # Given
        sub_theme_manager = SubThemeManager()

        # When
        sub_theme_manager.get_all_unique_names()

        # Then
        spy_get_all_unique_names.assert_called_once_with()

    @mock.patch.object(SubThemeQuerySet, "get_all_names_and_ids")
    def test_get_all_sub_theme_names(self, spy_get_all_names_and_ids: mock.MagicMock):
        """
        Given an instance of a `SubThemeManager`
        When `get_all_names` is called
        Then it delegates call to `SubThemeQuerySet`.
        """
        # Given
        sub_theme_manager = SubThemeManager()

        # When
        sub_theme_manager.get_all_names_and_ids()

        # Then
        spy_get_all_names_and_ids.assert_called_once_with()

    @mock.patch.object(SubThemeQuerySet, "get_filtered_unique_names_related_to_theme")
    def test_get_filtered_unique_names_related_to_theme(
        self, spy_get_filtered_unique_names_related_to_theme: mock.MagicMock
    ):
        """
        Given an instance of a `SubThemeManager`
        When `get_filtered_unique_names_related_to_theme` is called
        Then it delegates the call to `SubThemeQuerySet`
            with the given `parent_theme_id`
        """
        # Given
        sub_theme_manager = SubThemeManager()
        parent_theme_id = "123"

        # When
        sub_theme_manager.get_filtered_unique_names_related_to_theme(
            parent_theme_id=parent_theme_id
        )

        # Then
        spy_get_filtered_unique_names_related_to_theme.assert_called_once_with(
            parent_theme_id=parent_theme_id
        )
