import pytest

from metrics.data.models.rbac_models import RBACGroupPermission
from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACPermissionGroupFactory,
)


class TestRBACGroupPermissionFactory:
    group_permissions = {
        "name": "admin_group",
    }

    @pytest.mark.django_db
    def test_create_record_creates_valid_group_permission(self):
        """
        Given valid input parameters,
        When `create_record` is called,
        Then an `RBACGroupPermission` instance is created with the correct attributes.
        """
        # Given
        group_permission = RBACPermissionGroupFactory.create_record(
            **self.group_permissions
        )

        # When
        assert RBACGroupPermission.objects.filter(id=group_permission.id).exists()

        # Then
        assert group_permission.name == "admin_group"

    @pytest.mark.django_db
    def test_create_duplicate_group_permission_raises_error(self):
        """
        Given an existing `RBACGroupPermission` record with a specific name,
        When another group with the same name is created,
        Then an integrity error should be raised.
        """
        # Given
        RBACPermissionGroupFactory.create_record(name="admin_group")

        # When / Then
        with pytest.raises(Exception):  # Replace with the actual exception if needed
            RBACPermissionGroupFactory.create_record(name="admin_group")
