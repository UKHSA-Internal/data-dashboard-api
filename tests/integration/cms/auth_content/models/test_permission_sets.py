import pytest

from django.core.exceptions import ValidationError
from cms.auth_content.models.permission_sets import PermissionSet


class TestPermissionSet:
    @pytest.mark.django_db
    def test_validation_error_raised_if_queryset_duplicated(self):
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
            theme="1",
            sub_theme="2",
            topic="3",
            metric="4",
            geography_type="5",
            geography="6",
        )

        with pytest.raises(ValidationError) as e:
            permission_set.full_clean()

        assert "A matching permission set already exists: test permission set" in str(
            e.value
        )

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

        assert "Constraint “unique_non_null_display_name” is violated." in str(e.value)
