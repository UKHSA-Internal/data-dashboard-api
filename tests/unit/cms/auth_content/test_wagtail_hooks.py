from unittest.mock import MagicMock, patch
from django.test import TestCase
from django.utils.safestring import SafeData

from cms.auth_content.models.permission_sets import PermissionSet
from cms.auth_content.wagtail_hooks import (
    NoEditPermissionPolicy,
    PermissionSetViewSet,
    AuthGroup,
)
from cms.auth_content import wagtail_hooks


class TestWagtailHooks(TestCase):
    def test_register_auth_viewset(self):
        result = wagtail_hooks.register_auth_viewset()
        assert result.menu_label == AuthGroup.menu_label
        assert result.menu_icon == AuthGroup.menu_icon
        assert result.menu_order == AuthGroup.menu_order
        assert len(result.items) == 2


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

    @patch("wagtail.permission_policies.ModelPermissionPolicy.user_has_permission")
    def test_user_has_permission_calls_super(self, spy_user_has_permissions: MagicMock):
        spy_user_has_permissions.return_value = "parent_response"
        result = self.policy.user_has_permission(self.user, "view")

        spy_user_has_permissions.assert_called_once_with(self.user, "view")
        assert result == "parent_response"

    def test_change_permission_denied_for_instance(self):
        self.assertFalse(
            self.policy.user_has_permission_for_instance(
                self.user, "change", self.instance
            )
        )

    @patch(
        "wagtail.permission_policies.ModelPermissionPolicy.user_has_permission_for_instance"
    )
    def test_user_has_permission_for_instance_calls_super(
        self, spy_user_has_permissions_for_instance: MagicMock
    ):
        spy_user_has_permissions_for_instance.return_value = "parent_response"
        result = self.policy.user_has_permission_for_instance(
            self.user, "view", self.instance
        )

        spy_user_has_permissions_for_instance.assert_called_once_with(
            self.user, "view", self.instance
        )
        assert result == "parent_response"


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
