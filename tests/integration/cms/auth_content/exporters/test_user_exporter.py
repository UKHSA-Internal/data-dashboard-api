import uuid
from django.test import TestCase

from cms.auth_content.models.users import User
from cms.auth_content.models.permission_sets import PermissionSet
from cms.auth_content.exporters.user_exporter import (
    generate_user_permission_sets_csv_rows,
)


class TestUserCsvExporter(TestCase):
    def test_user_with_no_permission_sets_exports_as_blank_row(self):
        user = User.objects.create(user_id=uuid.uuid4())

        rows = list(generate_user_permission_sets_csv_rows(User.objects.all()))

        self.assertEqual(len(rows), 2)
        self.assertEqual(
            rows[0], "User ID,Permission Set,Gives Global Access,Permissions\r\n"
        )
        self.assertEqual(rows[1], f"{str(user.user_id)},,,\r\n")

    def test_export_with_multiple_users_and_permissions(self):
        # Results are sorted by user id, so hardcoding easier to determine uuids to ensure test order
        user_without_permissions = User.objects.create(
            user_id="11111111-1111-1111-1111-111111111111"
        )
        user_with_one_permission_set = User.objects.create(
            user_id="22222222-2222-2222-2222-222222222222"
        )
        user_with_two_permission_sets = User.objects.create(
            user_id="33333333-3333-3333-3333-333333333333"
        )
        global_access_permission_set = PermissionSet.objects.create(
            display_name="Global",
            theme="-1",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="-1",
        )
        limited_access_permission_set = PermissionSet.objects.create(
            display_name="Limited",
            theme="11",
            sub_theme="-1",
            topic="-1",
            metric="-1",
            geography_type="-1",
        )
        user_with_one_permission_set.permission_sets.add(limited_access_permission_set)
        user_with_two_permission_sets.permission_sets.add(
            global_access_permission_set, limited_access_permission_set
        )
        rows = list(generate_user_permission_sets_csv_rows(User.objects.all()))

        self.assertEqual(len(rows), 5)
        self.assertEqual(
            rows[0], "User ID,Permission Set,Gives Global Access,Permissions\r\n"
        )
        self.assertEqual(rows[1], f"{str(user_without_permissions.user_id)},,,\r\n")
        self.assertEqual(
            rows[2],
            f"{str(user_with_one_permission_set.user_id)},Limited,False,Theme: 11 | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All)\r\n",
        )
        self.assertEqual(
            rows[3],
            f"{str(user_with_two_permission_sets.user_id)},Global,True,Theme: * (All) | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All)\r\n",
        )
        self.assertEqual(
            rows[4],
            f"{str(user_with_two_permission_sets.user_id)},Limited,False,Theme: 11 | Sub-theme: * (All) | Topic: * (All) | Metric: * (All) | Geography Type: * (All)\r\n",
        )
