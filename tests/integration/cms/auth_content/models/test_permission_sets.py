import pytest
from django.db import models

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

    def test_unrecognised_validation_error_is_preserved(self):
        # Ensure validation errors unrelated to permission set uniqueness
        # are returned unchanged.
        error = ValidationError(
            "Other validation error",
            code="other_constraint",
        )

        permission_set = PermissionSet()

        assert permission_set._with_existing_set_name(error) is error

    def test_non_dict_validation_error_is_preserved(self, monkeypatch):
        # Simulate a validation error without a field-specific error
        # dictionary to ensure the original error is preserved.
        def raise_validation_error(instance, exclude=None):
            raise ValidationError("Other validation error")

        monkeypatch.setattr(
            models.Model,
            "validate_constraints",
            raise_validation_error,
        )

        permission_set = PermissionSet()

        with pytest.raises(ValidationError) as exc_info:
            permission_set.validate_constraints()

        assert exc_info.value.messages == ["Other validation error"]

    @pytest.mark.django_db
    def test_original_error_preserved_when_no_duplicate_exists(self):
        # Ensure the original validation error is retained when
        # no existing permission set matches the selected permissions.
        permission_set = PermissionSet(
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        error = ValidationError(
            "Original validation error",
            code="unique_together",
        )

        assert permission_set._with_existing_set_name(error) is error

    @pytest.mark.django_db
    def test_existing_permission_set_excludes_itself(self):
        # Ensure an existing permission set is excluded from its own
        # duplicate lookup to prevent false validation errors.
        permission_set = PermissionSet.objects.create(
            display_name="Existing permission set",
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        error = ValidationError(
            "Original validation error",
            code="unique_together",
        )

        assert permission_set._with_existing_set_name(error) is error
