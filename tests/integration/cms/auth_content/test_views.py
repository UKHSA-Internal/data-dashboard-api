import freezegun
from unittest import mock
import uuid
from django.test import TestCase
from django.urls import reverse

from cms.auth_content.models.users import User


class TestExportUserPermissionsView(TestCase):
    def setUp(self):
        self.mock_logger = mock.patch("cms.auth_content.views.audit_logger").start()
        self.addCleanup(mock.patch.stopall)
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

    @freezegun.freeze_time("2026-08-17 12:00:00")
    def test_export_user_permissions_view_response(self):
        User.objects.create(user_id=uuid.uuid4())
        url = reverse("export_user_permission_sets_csv")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(
            'attachment; filename="dashboard_cms_users_20260817-120000.csv"',
            response["Content-Disposition"],
        )

    def test_exporting_users_creates_audit_log(self):
        User.objects.create(user_id=uuid.uuid4())
        url = reverse("export_user_permission_sets_csv")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.mock_logger.info.assert_called_once()
        _, kwargs = self.mock_logger.info.call_args
        self.assertEqual(kwargs["extra"]["user"], self.superuser.id)
        self.assertEqual(kwargs["extra"]["action"], "CSV EXPORT")
        self.assertEqual(kwargs["extra"]["target"], "Users and permissions")
