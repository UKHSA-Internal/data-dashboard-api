import unittest
from unittest import mock

from metrics.data.managers.rbac_models.user import UserManager, UserQuerySet


class TestUserManager(unittest.TestCase):
    @mock.patch.object(UserQuerySet, "get_user_with_permission_sets")
    def test_get_all_theme_names_and_ids(
        self, spy_get_user_with_permission_sets: mock.MagicMock
    ):
        """
        Given an instance of a `UserManager`
        When `get_user_with_permission_sets` is called
        Then it delegates call to `UserQuerySet`.
        """
        # Given
        user_manager = UserManager()

        mock_user_id = 1

        # When
        user_manager.get_user_with_permission_sets(mock_user_id)

        # Then
        spy_get_user_with_permission_sets.assert_called_once()
