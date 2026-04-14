from unittest.mock import MagicMock
from django.test import TestCase
from django.utils.safestring import SafeData

from auth_content.models import PermissionSet
from auth_content.wagtail_hooks import NoEditPermissionPolicy, PermissionSetViewSet


class TestPermissionSetDetailsProperty(TestCase):

    def test_single_value_no_pipe(self):
        permission_set = PermissionSet(name="test 1")
        self.assertEqual(permission_set.permission_set_details, "test 1")

    def test_pipe_separated_values_split_to_newlines(self):
        permission_set = PermissionSet(name="Name One|Name Two|Name Three")
        self.assertEqual(
            permission_set.permission_set_details, "Name One<br>Name Two<br>Name Three"
        )

    def test_whitespace_around_pipes_is_stripped(self):
        permission_set = PermissionSet(name="Name One | Name Two")
        self.assertEqual(permission_set.permission_set_details, "Name One<br>Name Two")

    def test_empty_string(self):
        permission_set = PermissionSet(name="")
        self.assertEqual(permission_set.permission_set_details, "")

    def test_output_is_marked_safe(self):
        permission_set = PermissionSet(name="Name One|Name Two")
        self.assertIsInstance(permission_set.permission_set_details, SafeData)


class TestNoEditPermissionPolicy(TestCase):

    def setUp(self):
        self.policy = NoEditPermissionPolicy(PermissionSet)
        self.user = MagicMock()
        self.instance = PermissionSet(name="Test")

    def test_change_permission_denied(self):
        self.assertFalse(self.policy.user_has_permission(self.user, "change"))

    def test_change_permission_denied_for_instance(self):
        self.assertFalse(
            self.policy.user_has_permission_for_instance(
                self.user, "change", self.instance
            )
        )


class TestPermissionSetViewSet(TestCase):

    def setUp(self):
        self.viewset = PermissionSetViewSet()

    def test_inspect_view_fields_contains_permission_set_details(self):
        self.assertIn("permission_set_details", self.viewset.inspect_view_fields)

    def test_permission_policy_is_no_edit_policy(self):
        self.assertIsInstance(self.viewset.permission_policy, NoEditPermissionPolicy)

    def test_change_permission_denied_via_viewset_policy(self):
        user = MagicMock()
        self.assertFalse(
            self.viewset.permission_policy.user_has_permission(user, "change")
        )
