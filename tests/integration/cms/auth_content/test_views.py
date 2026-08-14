import uuid
from django.test import TestCase
from django.urls import reverse

from cms.auth_content.models.users import User

class TestExportUserPermissionsView(TestCase):
    def setUp(self):
        self.superuser = self._create_superuser()
        self.client.force_login(self.superuser)

    @staticmethod
    def _create_superuser():
        from django.contrib.auth import get_user_model

        AdminUser = get_user_model()
        return AdminUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )

    def test_export_requires_login(self):
        self.client.logout()
        url = reverse("export_user_permission_sets_csv")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_export_user_permissions_view_response(self):
        User.objects.create(user_id=uuid.uuid4())
        url = reverse("export_user_permission_sets_csv")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(
            'attachment; filename="dashboard_cms_users.csv"',
            response["Content-Disposition"],
        )

    # TODO: Do we need to test the CSV contents as well or is the other test case enough?
