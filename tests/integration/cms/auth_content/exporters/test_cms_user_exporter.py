import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils


@pytest.mark.django_db
class Test(TestCase, WagtailTestUtils):

    def setUp(self):
        super().setUp()
        # non admin user
        self.regular_user = User.objects.create_user(
            username="regular_user", password="password"
        )

        # admin user
        self.admin_user = User.objects.create_superuser(
            username="admin_user", password="password"
        )

        self.target_url = reverse("export_user_permission_sets_csv")


    def test_action_forbidden_to_non_admin(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.target_url)
        assert response.status_code == 302


    def test_action_is_allowed_for_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.target_url)
        assert response.status_code == 200