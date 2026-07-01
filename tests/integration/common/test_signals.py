import uuid
from unittest import mock

from django.test import TestCase

from cms.auth_content.models.users import User
from cms.auth_content.models.permission_sets import PermissionSet


def make_user(user_id=None, pk=None):
    """Build a real (unsaved) User instance to use as before/after state."""
    return User(pk=pk, user_id=user_id or uuid.uuid4())


class FakeUser:
    """Stand-in for a request.user, avoiding a real auth User."""

    def __init__(self, id_=1, is_authenticated=True):
        self.id = id_
        self.is_authenticated = is_authenticated


def through_model(name):
    """A throwaway class whose __name__ mimics an m2m 'through' model."""
    return type(name, (), {})


class SignalWiringIntegrationTests(TestCase):
    def setUp(self):
        self.mock_logger = mock.patch("common.signals.audit_logger").start()
        self.addCleanup(mock.patch.stopall)
        self.mock_get_user = mock.patch("common.signals.get_current_user").start()
        self.mock_get_user.return_value = FakeUser(id_=1)

    def test_creating_user_logs_once(self):
        User.objects.create(user_id=uuid.uuid4())
        self.assertEqual(self.mock_logger.info.call_count, 1)
        args, kwargs = self.mock_logger.info.call_args
        self.assertEqual(args[0], "Model saved")
        self.assertEqual(kwargs["extra"]["action"], "CREATED User")

    def test_updating_a_field_logs_the_diff(self):
        user = User.objects.create(user_id=uuid.uuid4())
        self.mock_logger.reset_mock()

        new_id = uuid.uuid4()
        user.user_id = new_id
        user.save()

        self.mock_logger.info.assert_called_once()
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["action"], "UPDATED User")
        self.assertIn(str(new_id), kwargs["extra"]["target"])

    def test_saving_with_no_actual_changes_does_not_log(self):
        user = User.objects.create(user_id=uuid.uuid4())
        self.mock_logger.reset_mock()

        user.save()

        self.mock_logger.info.assert_not_called()

    def test_deleting_user_logs_once(self):
        user = User.objects.create(user_id=uuid.uuid4())
        self.mock_logger.reset_mock()

        user.delete()

        self.mock_logger.info.assert_called_once()
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["action"], "DELETE User")

    def test_adding_a_permission_set_logs_relationship_change_only_once(self):
        user = User.objects.create(user_id=uuid.uuid4())
        permission_set = PermissionSet.objects.create()
        self.mock_logger.reset_mock()

        user.permission_sets.add(permission_set)

        # Exactly one log: the m2m relationship add. No duplicate
        # "User UPDATED" log should fire for the same change.
        self.mock_logger.info.assert_called_once()
        _, kwargs = self.mock_logger.info.call_args
        self.assertIn("ADD User_permission_sets", kwargs["extra"]["action"])

    def test_removing_a_permission_set_logs_relationship_change_only_once(self):
        user = User.objects.create(user_id=uuid.uuid4())
        permission_set = PermissionSet.objects.create()
        user.permission_sets.add(permission_set)
        self.mock_logger.reset_mock()

        user.permission_sets.remove(permission_set)

        self.mock_logger.info.assert_called_once()
        _, kwargs = self.mock_logger.info.call_args
        self.assertIn("REMOVE User_permission_sets", kwargs["extra"]["action"])

    def test_clearing_permission_sets_logs_relationship_change_only_once(self):
        user = User.objects.create(user_id=uuid.uuid4())
        permission_set = PermissionSet.objects.create()
        user.permission_sets.add(permission_set)
        self.mock_logger.reset_mock()

        user.permission_sets.clear()

        self.mock_logger.info.assert_called_once()
        _, kwargs = self.mock_logger.info.call_args
        self.assertIn("CLEAR User_permission_sets", kwargs["extra"]["action"])

    def test_permission_set_changes_are_also_audited(self):
        permission_set = PermissionSet.objects.create()
        self.mock_logger.reset_mock()

        permission_set.display_name = "changed"
        permission_set.save()
        permission_set.delete()

        self.assertEqual(self.mock_logger.info.call_count, 2)
        actions = [
            call.kwargs["extra"]["action"]
            for call in self.mock_logger.info.call_args_list
        ]
        self.assertEqual(actions, ["UPDATED PermissionSet", "DELETE PermissionSet"])
