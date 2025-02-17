import pytest
from metrics.data.models.rbac_models import (
    RBACPermission,
    AdminFormDuplicatePermissionError,
)
from tests.factories.metrics.rbac_models.rbac_permission import ApiPermissionFactory


class TestApiPermissionFactory:

    permissions = {
        "theme_name": "infectious_disease",
        "sub_theme_name": "respiratory",
        "topic_name": "COVID-19",
        "metric_name": "COVID-19_headline_positivity_latest",
        "geography_type_name": "Nation",
        "geography_name": "England",
        "stratum_name": "default",
        "age_name": "all",
    }

    @pytest.mark.django_db
    def test_create_record_creates_valid_permission(self):
        """
        Given valid input parameters,
        When `create_record` is called,
        Then an `RBACPermission` instance is created with the correct associations.
        """
        # When creating a permission record
        permission = ApiPermissionFactory.create_record(**self.permissions)

        # Then the permission should exist in the database
        assert RBACPermission.objects.filter(id=permission.id).exists()

        # And the related objects should be correctly associated
        assert permission.theme.name == "infectious_disease"
        assert permission.sub_theme.name == "respiratory"
        assert permission.topic.name == "COVID-19"
        assert permission.metric.name == "COVID-19_headline_positivity_latest"
        assert permission.geography.name == "England"
        assert permission.geography_type.name == "Nation"
        assert permission.stratum.name == "default"
        assert permission.age.name == "all"

    @pytest.mark.django_db
    def test_get_existing_permissions_returns_no_queryset(self):
        """
        Given multiple `RBACPermission` records with overlapping fields
        And a unique `RBACPermission` record
        When `get_existing_permissions()` is called
        Then only the records with matching fields (excluding the given instance) are returned
        """
        # Given creating an initial permission
        permission = ApiPermissionFactory.create_record()

        # Create another permission with different `name`, `theme` & `sub_theme` (to ensure uniqueness)
        _ = ApiPermissionFactory.create_record(
            name=f"permission_2",
            theme_name="extreme_event",
            sub_theme_name="weather_alert",
        )
        # When fetching existing permissions
        retrieved_permissions = RBACPermission.objects.get_existing_permissions(
            permission
        )

        # Then it should only return the matching permission, excluding itself
        assert retrieved_permissions.count() == 0

    @pytest.mark.django_db
    def test_create_duplicate_permission_raises_error(self):
        """
        Given an existing `RBACPermission` record with specific fields,
        When another permission with the same fields is created,
        Then an `AdminFormDuplicatePermissionError` should be raised.
        """
        # Given Create an initial permission
        ApiPermissionFactory.create_record(
            name="permission_1",
            theme_name="infectious_disease",
            sub_theme_name="respiratory",
        )

        # When / Then Creating a duplicate permission should raise an error
        # with different name, but same unique fields
        with pytest.raises(AdminFormDuplicatePermissionError):
            ApiPermissionFactory.create_record(
                name="permission_2",
                theme_name="infectious_disease",
                sub_theme_name="respiratory",
            )
