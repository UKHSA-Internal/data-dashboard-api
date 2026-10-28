import pytest
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from wagtail.test.utils import WagtailTestUtils


@pytest.mark.django_db
class Test(TestCase, WagtailTestUtils):

    def setUp(self):
        super().setUp()

        # groups
        moderators_group = Group.objects.get_or_create(name="Moderators")[0]
        editors_group = Group.objects.get_or_create(name="Editors")[0]

        # non admin user
        self.regular_user = self.create_user(
            username="regular_user", password="password", is_staff=True
        )

        # admin user
        self.admin_user = self.create_superuser(
            username="admin_user",
            password="password",
        )

        # moderator user
        self.moderator_user = self.create_user(
            username="moderator_user", password="password", is_staff=True
        )
        self.moderator_user.groups.add(moderators_group)

        # editor user
        self.editors_user = self.create_user(
            username="editors_user", password="password", is_staff=True
        )
        self.editors_user.groups.add(editors_group)

        self.target_url = reverse("export_user_permission_sets_csv")

    def test_action_is_redirected_to_login_page_for_public(self):
        self.client.logout()  # Make sure no leftover session muddles the test
        response = self.client.get(self.target_url)
        assert response.status_code == 302

    def test_action_redirected_to_login_page_for_non_admin(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.target_url)
        assert response.status_code == 302

    def test_action_is_allowed_for_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.target_url)
        assert response.status_code == 200

    def test_action_is_permission_denied_for_moderator(self):
        self.client.force_login(self.moderator_user)
        response = self.client.get(self.target_url)
        assert response.status_code == 302

    def test_action_is_permission_denied_for_editor(self):
        self.client.force_login(self.editors_user)
        response = self.client.get(self.target_url)
        assert response.status_code == 302
