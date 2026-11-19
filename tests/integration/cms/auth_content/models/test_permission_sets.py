import pytest

from django.core.exceptions import ValidationError
from cms.auth_content.models.permission_sets import PermissionSet


class TestPermissionSet:
    @pytest.mark.django_db
    def test_validation_error_raised_if_queryset_duplicated(self):
        original = PermissionSet.objects.create(
            display_name="test permission set",
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        permission_set = PermissionSet(
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        with pytest.raises(ValidationError) as e:
            permission_set.full_clean()

        expected_message = (
            "A permission set comprising the same unique permissions combination "
            f"already exists called “{original.display_name}”. "
            "Permission sets must represent a unique combination of permissions."
        )

        assert expected_message in e.value.messages

    @pytest.mark.django_db
    def test_validation_error_raised_if_queryset_duplicated_without_display_name(self):
        original = PermissionSet.objects.create(
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        permission_set = PermissionSet(
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        with pytest.raises(ValidationError) as e:
            permission_set.full_clean()

        expected_message = (
            "A permission set comprising the same unique permissions combination "
            f"already exists called “{original.name}”. "
            "Permission sets must represent a unique combination of permissions."
        )

        assert expected_message in e.value.messages

    @pytest.mark.django_db
    def test_validation_error_raised_if_name_duplicated(self):
        PermissionSet.objects.create(
            display_name="test permission set",
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        permission_set = PermissionSet(
            display_name="test permission set",
            theme="1",
            sub_theme="2",
            topic="3",
            metric="9",
            geography_type="5",
            geography="9",
        )

        with pytest.raises(ValidationError) as e:
            permission_set.full_clean()

        expected_message = (
            "A permission set with the name “test permission set” already exists. "
            "Permission sets must have unique names."
        )

        assert e.value.messages == [expected_message]
        assert "unique_non_null_display_name" not in str(e.value)

    @pytest.mark.django_db
    def test_validation_errors_if_name_and_permissions_duplicated(self):
        original = PermissionSet.objects.create(
            display_name="test permission set",
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        permission_set = PermissionSet(
            display_name="test permission set",
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        with pytest.raises(ValidationError) as e:
            permission_set.full_clean()

        expected_permissions_message = (
            "A permission set comprising the same unique permissions combination "
            f"already exists called “{original.display_name}”. "
            "Permission sets must represent a unique combination of permissions."
        )

        expected_name_message = (
            f"A permission set with the name “{original.display_name}” already exists. "
            "Permission sets must have unique names."
        )

        assert len(e.value.messages) == 2
        assert expected_permissions_message in e.value.messages
        assert expected_name_message in e.value.messages
        assert "unique_non_null_display_name" not in str(e.value)
