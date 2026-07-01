import uuid
from unittest import mock

from django.test import SimpleTestCase

from cms.auth_content.models.users import User
from cms.auth_content.models.api_application import APIApplication
from common.signals import (
    audit_delete_log,
    audit_m2m_relationships_log,
    audit_save_log,
    track_concrete_field_changes,
)


def make_user(user_id=None, pk=None):
    """Build a real (unsaved) User instance to use as before/after state."""
    return User(pk=pk, user_id=user_id or uuid.uuid4())


class FakeUser:
    """Stand-in for a request.user, avoiding a real auth User/DB hit."""
    def __init__(self, id_=1, is_authenticated=True):
        self.id = id_
        self.is_authenticated = is_authenticated


def through_model(name):
    """A throwaway class whose __name__ mimics an m2m 'through' model."""
    return type(name, (), {})


class TrackConcreteFieldChangesTests(SimpleTestCase):
    def test_non_auditable_model_is_skipped(self):
        instance = mock.Mock(spec=[])
        track_concrete_field_changes(sender=through_model("Foo"), instance=instance)
        self.assertFalse(hasattr(instance, "audit_fields_changed"))
        self.assertFalse(hasattr(instance, "audit_field_diff"))

    def test_new_instance_without_pk_is_treated_as_changed(self):
        instance = User(user_id=uuid.uuid4())
        track_concrete_field_changes(sender=User, instance=instance)
        self.assertTrue(instance.audit_fields_changed)
        self.assertEqual(instance.audit_field_diff, {})

    def test_pk_set_but_row_missing_is_treated_as_changed(self):
        instance = make_user(pk=99)
        with mock.patch.object(User.objects, "get", side_effect=User.DoesNotExist):
            track_concrete_field_changes(sender=User, instance=instance)
        self.assertTrue(instance.audit_fields_changed)
        self.assertEqual(instance.audit_field_diff, {})

    def test_no_changes_detected(self):
        user_id = uuid.uuid4()
        stored = make_user(pk=1, user_id=user_id)
        instance = make_user(pk=1, user_id=user_id)
        with mock.patch.object(User.objects, "get", return_value=stored):
            track_concrete_field_changes(sender=User, instance=instance)
        self.assertFalse(instance.audit_fields_changed)
        self.assertEqual(instance.audit_field_diff, {})

    def test_changed_field_is_captured_as_old_new_pair(self):
        old_user_id, new_user_id = uuid.uuid4(), uuid.uuid4()
        stored = make_user(pk=1, user_id=old_user_id)
        instance = make_user(pk=1, user_id=new_user_id)
        with mock.patch.object(User.objects, "get", return_value=stored):
            track_concrete_field_changes(sender=User, instance=instance)
        self.assertTrue(instance.audit_fields_changed)
        self.assertEqual(
            instance.audit_field_diff,
            {"user_id": (old_user_id, new_user_id)},
        )

    def test_update_fields_restricts_diff_to_named_fields(self):
        stored = APIApplication(
            pk=1, application_id=uuid.uuid4(), application_name="Old", is_active=True
        )
        instance = APIApplication(
            pk=1, application_id=uuid.uuid4(), application_name="New", is_active=False
        )
        with mock.patch.object(APIApplication.objects, "get", return_value=stored):
            track_concrete_field_changes(
                sender=APIApplication,
                instance=instance,
                update_fields=["application_name"],
            )
        self.assertEqual(
            instance.audit_field_diff, {"application_name": ("Old", "New")}
        )
        self.assertNotIn("application_id", instance.audit_field_diff)
        self.assertNotIn("is_active", instance.audit_field_diff)

    def test_update_fields_silently_drops_m2m_field_names(self):
        stored = APIApplication(pk=1, application_name="Same")
        instance = APIApplication(pk=1, application_name="Same")
        with mock.patch.object(APIApplication.objects, "get", return_value=stored):
            # "permission_sets" is m2m; must not raise or be diffed.
            track_concrete_field_changes(
                sender=APIApplication,
                instance=instance,
                update_fields=["application_name", "permission_sets"],
            )
        self.assertEqual(instance.audit_field_diff, {})
        self.assertFalse(instance.audit_fields_changed)


class AuditM2MRelationshipsLogTests(SimpleTestCase):
    def setUp(self):
        self.mock_logger = mock.patch("common.signals.audit_logger").start()
        self.addCleanup(mock.patch.stopall)
        self.mock_get_user = mock.patch("common.signals.get_current_user").start()
        self.mock_get_user.return_value = FakeUser(id_=7)

    def test_non_auditable_relationship_is_ignored(self):
        audit_m2m_relationships_log(
            sender=through_model("Foo_bar"),
            instance=User(pk=1),
            action="post_add",
            pk_set={1},
        )
        self.mock_logger.info.assert_not_called()

    def test_pre_add_action_is_ignored(self):
        audit_m2m_relationships_log(
            sender=through_model("User_permission_sets"),
            instance=User(pk=1),
            action="pre_add",
            pk_set={1},
        )
        self.mock_logger.info.assert_not_called()

    def test_post_add_logs_expected_message(self):
        user_id = uuid.uuid4()
        audit_m2m_relationships_log(
            sender=through_model("User_permission_sets"),
            instance=User(pk=1, user_id=user_id),
            action="post_add",
            pk_set={5},
        )
        self.mock_logger.info.assert_called_once_with(
            "User permission sets relationship added",
            extra={
                "user": 7,
                "action": "ADD User_permission_sets {5}",
                "target": f"pk=1, id={user_id}",
            },
        )

    def test_post_remove_logs_expected_message(self):
        audit_m2m_relationships_log(
            sender=through_model("APIApplication_permission_sets"),
            instance=APIApplication(pk=2),
            action="post_remove",
            pk_set={9},
        )
        self.mock_logger.info.assert_called_once_with(
            "User permission sets relationship removed",
            extra={
                "user": 7,
                "action": "REMOVE APIApplication_permission_sets {9}",
                "target": "pk=2",
            },
        )

    def test_post_clear_logs_expected_message(self):
        user_id = uuid.uuid4()
        audit_m2m_relationships_log(
            sender=through_model("User_permission_sets"),
            instance=User(pk=3, user_id=user_id),
            action="post_clear",
            pk_set=None,
        )
        self.mock_logger.info.assert_called_once_with(
            "User permission sets relationships cleared",
            extra={
                "user": 7,
                "action": "CLEAR User_permission_sets",
                "target": f"pk=3, id={user_id}",
            },
        )

    def test_unauthenticated_user_is_logged_as_anonymous(self):
        self.mock_get_user.return_value = FakeUser(is_authenticated=False)
        audit_m2m_relationships_log(
            sender=through_model("User_permission_sets"),
            instance=User(pk=1),
            action="post_add",
            pk_set={1},
        )
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["user"], "anonymous")

    def test_no_current_user_is_logged_as_anonymous(self):
        self.mock_get_user.return_value = None
        audit_m2m_relationships_log(
            sender=through_model("User_permission_sets"),
            instance=User(pk=1),
            action="post_add",
            pk_set={1},
        )
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["user"], "anonymous")


class AuditSaveLogTests(SimpleTestCase):
    def setUp(self):
        self.mock_logger = mock.patch("common.signals.audit_logger").start()
        self.addCleanup(mock.patch.stopall)
        self.mock_get_user = mock.patch("common.signals.get_current_user").start()
        self.mock_get_user.return_value = FakeUser(id_=3)

    def test_non_auditable_model_is_ignored(self):
        audit_save_log(sender=through_model("Foo"), instance=mock.Mock(), created=True)
        self.mock_logger.info.assert_not_called()

    def test_create_is_logged(self):
        user_id = uuid.uuid4()
        instance = User(pk=10, user_id=user_id)
        audit_save_log(sender=User, instance=instance, created=True)
        self.mock_logger.info.assert_called_once_with(
            "Model saved",
            extra={"user": 3, "action": "CREATED User", "target": f"pk=10, id={user_id}"},
        )

    def test_update_with_no_changes_is_not_logged(self):
        instance = User(pk=10, user_id=uuid.uuid4())
        instance.audit_fields_changed = False
        instance.audit_field_diff = {}
        audit_save_log(sender=User, instance=instance, created=False)
        self.mock_logger.info.assert_not_called()

    def test_update_with_changes_logs_old_and_new_values(self):
        old_id, new_id = uuid.uuid4(), uuid.uuid4()
        instance = User(pk=10, user_id=new_id)
        instance.audit_fields_changed = True
        instance.audit_field_diff = {"user_id": (str(old_id), str(new_id))}
        audit_save_log(sender=User, instance=instance, created=False)
        self.mock_logger.info.assert_called_once_with(
            "Model saved",
            extra={
                "user": 3,
                "action": "UPDATED User",
                "target": (
                    f"pk=10, id={new_id}, Changes: "
                    f"{{'user_id': {{'old': '{old_id}', 'new': '{new_id}'}}}}"
                ),
            },
        )

    def test_missing_audit_fields_changed_defaults_to_logging(self):
        instance = User(pk=10, user_id=uuid.uuid4())
        audit_save_log(sender=User, instance=instance, created=False)
        self.mock_logger.info.assert_called_once()

    def test_no_current_user_is_logged_as_anonymous(self):
        self.mock_get_user.return_value = None
        instance = User(pk=10, user_id=uuid.uuid4())
        audit_save_log(sender=User, instance=instance, created=True)
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["user"], "anonymous")


class AuditDeleteLogTests(SimpleTestCase):
    def setUp(self):
        self.mock_logger = mock.patch("common.signals.audit_logger").start()
        self.addCleanup(mock.patch.stopall)
        self.mock_get_user = mock.patch("common.signals.get_current_user").start()
        self.mock_get_user.return_value = FakeUser(id_=4)

    def test_non_auditable_model_is_ignored(self):
        audit_delete_log(sender=through_model("Foo"), instance=mock.Mock())
        self.mock_logger.info.assert_not_called()

    def test_delete_is_logged(self):
        instance = APIApplication(pk=8)
        audit_delete_log(sender=APIApplication, instance=instance)
        self.mock_logger.info.assert_called_once_with(
            "Model deleted",
            extra={"user": 4, "action": "DELETE APIApplication", "target": "pk=8"},
        )

    def test_no_current_user_is_logged_as_anonymous(self):
        self.mock_get_user.return_value = None
        instance = APIApplication(pk=8)
        audit_delete_log(sender=APIApplication, instance=instance)
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["user"], "anonymous")
